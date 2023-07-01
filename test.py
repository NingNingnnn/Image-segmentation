import torch
import torch.nn.functional as F
from torch.autograd import Variable
from dataset import MyTestData
from model import Deconv
import densenet
import numpy as np
import os
import sys
import argparse
import time
from PIL import Image




home = os.path.expanduser("~")

parser = argparse.ArgumentParser()
parser.add_argument('--input_dir', default='input')  # test dataset
parser.add_argument('--output_dir', default='mask')  # test dataset
parser.add_argument('--para_dir', default='parameters')  # parameters
parser.add_argument('--b', type=int, default=1)  # batch size
parser.add_argument('--q', default='densenet121')  # save checkpoint parameters
opt = parser.parse_args()
print(opt)



def main():
    """
    主函数，用于加载模型，数据，进行预测和保存结果
    """
    if not os.path.exists(opt.output_dir):
        os.mkdir(opt.output_dir)
    bsize = opt.b

    feature = getattr(densenet, opt.q)(pretrained=False)# 根据参数q获取densenet模型的特征提取部分，并不加载预训练权重
    feature.cuda()# 将模型移动到GPU上
    feature.eval()# 将模型设置为评估模式，不更新梯度和权重
    sb = torch.load(r'parameters_densenet121\feature_model.pth')# 加载特征提取部分的参数

    feature.load_state_dict(sb)# 将参数加载到模型中

    deconv = Deconv(opt.q)# 创建一个Deconv类的实例，用于对特征进行反卷积操作，生成掩码输出
    deconv.cuda()# 将模型移动到GPU上
    deconv.eval()# 将模型设置为评估模式，不更新梯度和权重
    sb = torch.load(r'parameters_densenet121\deconv_model.pth')# 加载反卷积部分的参数

    deconv.load_state_dict(sb)
    test_loader = torch.utils.data.DataLoader(MyTestData(opt.input_dir), batch_size=bsize, shuffle=False, num_workers=1, pin_memory=True)

    step_len = len(test_loader)
    for id, (data, img_name, img_size) in enumerate(test_loader):# 遍历每个批次的数据，获取图像数据，图像名称和图像大小
        inputs = Variable(data).cuda()
        start_time = time.time()# 记录开始时间
        feats = feature(inputs)# 用特征提取部分对输入进行处理，得到特征张量
        outputs = deconv(feats)# 对输出张量进行sigmoid激活函数，将值映射到0-1之间，表示掩码的概率值
        outputs = F.sigmoid(outputs)# 对输出张量进行sigmoid激活函数，将值映射到0-1之间，表示掩码的概率值
        outputs = outputs.data.cpu().squeeze(1).numpy()# 将输出张量从GPU移动到CPU上，并转换为numpy数组，并去掉第二个维度（通道维度）
        end_time = time.time()# 记录结束时间

        for i, msk in enumerate(outputs):
            msk = (msk * 255).astype(np.uint8)# 将掩码值乘以255，并转换为无符号8位整数类型，表示灰度值（0-255）
            msk = Image.fromarray(msk)# 将掩码数组转换为图像对象
            msk = msk.resize((img_size[0][i], img_size[1][i]))# 将掩码图像大小调整为原始图像大小
            msk.save('%s\\%s.png' % (opt.output_dir, img_name[i]), 'PNG')# 保存掩码图像到输出目录，文件名和格式与原始图像相同

        # 显示进度
        step_now = id + 1
        step_schedule_num = int(40 * step_now / step_len)
        print("\r", end="")
        print("step: {}/{} [{}{}] - time: {:.2f}ms".format(step_now, step_len, # 计算进度条的长度（40个字符）
                                                           ">" * step_schedule_num,
                                                           "-" * (40 - step_schedule_num),
                                                           (end_time - start_time) * 1000), end="") # 打印进度条，当前批次，总批次，用时等信息

        sys.stdout.flush()# 刷新输出缓冲区

    print("\r")


if __name__ == "__main__":
    main()
