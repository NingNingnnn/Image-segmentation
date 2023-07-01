import gc
import torch
import torch.nn.functional as F
from torch.autograd import Variable
from dataset import MyData
from model import Deconv
import densenet
import os
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--train_dir', default=r'D:\projects\github\source\images\data\train')  # training dataset
parser.add_argument('--val_dir', default=r'D:\projects\github\source\images\data\test')  # test dataset
parser.add_argument('--check_dir', default=r'D:\projects\github\source\parameters')  # save checkpoint parameters
parser.add_argument('--q', default='densenet121')  # save checkpoint parameters
parser.add_argument('--b', type=int, default=12)  # batch size
parser.add_argument('--e', type=int, default=20)  # epoches
parser.add_argument('--svae_interval', type=int, default=1)  # svae interval
opt = parser.parse_args()


def validation(feature, net, loader):
    """
    用于验证模型的性能，计算验证数据集上的损失值
    feature: 特征提取部分的模型
    net: 反卷积部分的模型
    loader: 验证数据集的加载器
    """
    feature.eval() # 将特征提取部分设置为评估模式，不更新梯度和权重
    net.eval() # 将反卷积部分设置为评估模式，不更新梯度和权重
    total_loss = 0 # 定义一个总损失值，初始为0
    for ib, (data, lbl) in enumerate(loader): # 遍历每个批次的数据，获取图像数据和标签数据
        inputs = Variable(data).cuda() # 将图像数据转换为变量，并移动到GPU上
        lbl = Variable(lbl.float().unsqueeze(1)).cuda() # 将标签数据转换为浮点数类型，并增加一个维度（通道维度），并移动到GPU上

        feats = feature(inputs) # 用特征提取部分对输入进行处理，得到特征张量
        msk = net(feats) # 用反卷积部分对特征张量进行处理，得到输出张量

        loss = F.binary_cross_entropy_with_logits(msk, lbl) # 计算输出张量和标签张量之间的二元交叉熵损失
        total_loss += loss.item() # 将损失值累加到总损失值上
    feature.train() # 将特征提取部分设置为训练模式，更新梯度和权重
    net.train() # 将反卷积部分设置为训练模式，更新梯度和权重
    return total_loss / len(loader) # 返回总损失值除以批次数量，得到平均损失值



def main():
    """
    主函数，用于训练模型，验证模型，保存模型
    """
    train_dir = opt.train_dir # 获取训练数据集的目录
    val_dir = opt.val_dir # 获取验证数据集的目录
    check_dir = opt.check_dir + '_' + opt.q # 获取保存模型参数的目录，根据参数q添加后缀
    bsize = opt.b # 获取批量大小
    epoch_sum = opt.e # 获取训练的总轮数
    svae_interval = opt.svae_interval # 获取保存模型参数的间隔轮数

    if not os.path.exists(check_dir):
        os.mkdir(check_dir) # 如果保存模型参数的目录不存在，创建一个新的目录

    feature = getattr(densenet, opt.q)(pretrained=True) # 根据参数q获取densenet模型的特征提取部分，并加载预训练权重
    feature.cuda() # 将模型移动到GPU上
    deconv = Deconv(opt.q) # 创建一个Deconv类的实例，用于对特征进行反卷积操作，生成掩码输出
    deconv.cuda() # 将模型移动到GPU上

    train_loader = torch.utils.data.DataLoader(MyData(train_dir, transform=True, crop=False, hflip=False, vflip=False),
                                               batch_size=bsize, shuffle=True, num_workers=1, pin_memory=True) # 创建一个数据加载器，用于加载训练数据集，设置转换，裁剪，翻转等选项
    val_loader = torch.utils.data.DataLoader(MyData(val_dir,  transform=True, crop=False, hflip=False, vflip=False),
                                             batch_size=bsize, shuffle=False, num_workers=1, pin_memory=True) # 创建一个数据加载器，用于加载验证数据集，设置转换，裁剪，翻转等选项

    optimizer = torch.optim.AdamW([
        {'params': feature.parameters(), 'lr': 8e-5}, # 设置特征提取部分的优化器参数，包括学习率
        {'params': deconv.parameters(), 'lr': 9e-5}, # 设置反卷积部分的优化器参数，包括学习率
    ]) # 创建一个AdamW优化器，用于更新模型参数

    min_loss = 10000.0 # 定义一个最小损失值，用于保存最佳模型参数
    for it in range(epoch_sum): # 遍历每一轮训练
        step_len = len(train_loader) # 获取数据加载器的长度，即批次的数量
        for ib, (data, lbl) in enumerate(train_loader): # 遍历每个批次的数据，获取图像数据和标签数据
            inputs = Variable(data).cuda() # 将图像数据转换为变量，并移动到GPU上
            lbl = Variable(lbl.float().unsqueeze(1)).cuda() # 将标签数据转换为浮点数类型，并增加一个维度（通道维度），并移动到GPU上
            feats = feature(inputs) # 用特征提取部分对输入进行处理，得到特征张量
            msk = deconv(feats) # 用反卷积部分对特征张量进行处理，得到输出张量
            loss = F.binary_cross_entropy_with_logits(msk, lbl) # 计算输出张量和标签张量之间的二元交叉熵损失

            deconv.zero_grad() # 将反卷积部分的梯度清零
            feature.zero_grad() # 将特征提取部分的梯度清零

            loss.backward() # 反向传播计算梯度

            optimizer.step() # 更新模型参数

            # 显示进度
            step_now = ib + 1 # 获取当前的批次编号
            step_schedule_num = int(40 * step_now / step_len) # 计算进度条的长度（40个字符）
            epoch_now = it + 1 # 获取当前的轮数编号
            print("\r", end="")
            print("epoch: {}/{} step: {}/{} [{}{}] - loss: {:.5f}".format(epoch_now, epoch_sum,
                                                                          step_now, step_len,
                                                                          ">" * step_schedule_num,
                                                                          "-" * (40 - step_schedule_num),
                                                                          loss.item()), end="") # 打印进度条，当前轮数，总轮数，当前批次，总批次，损失值等信息
            sys.stdout.flush() # 刷新输出缓冲区

            # 清除变量和内存
            del inputs, msk, lbl, loss, feats
            gc.collect() # 调用垃圾回收器，释放内存

        print("\r")

        if epoch_now % svae_interval == 0: # 如果当前轮数是保存间隔的倍数
            val_loss = validation(feature, deconv, val_loader) # 调用validation函数，用验证数据集计算模型的损失值
            if val_loss < min_loss: # 如果验证损失值小于最小损失值
                filename = ('{}/deconv_model.pth'.format(check_dir)) # 定义反卷积部分的参数文件名
                torch.save(deconv.state_dict(), filename) # 保存反卷积部分的参数到文件中
                filename = ('{}/feature_model.pth'.format(check_dir)) # 定义特征提取部分的参数文件名
                torch.save(feature.state_dict(), filename) # 保存特征提取部分的参数到文件中
                print('epoch: {} val loss: {:.5f} save model'.format(epoch_now, val_loss)) # 打印当前轮数，验证损失值，保存模型的信息
                min_loss = val_loss # 更新最小损失值为当前验证损失值
            else: # 如果验证损失值不小于最小损失值
                print('epoch: {} val loss: {:.5f} pass'.format(epoch_now, val_loss)) # 打印当前轮数，验证损失值，跳过保存模型的信息


if __name__ == "__main__":
    main() # 调用主函数
