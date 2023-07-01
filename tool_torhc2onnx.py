import torch
import os
import densenet
from model import Deconv
import argparse

# 文件绝对地址
Absolute_File_Path = os.path.dirname(__file__).replace('\\', '/') # 获取当前文件的绝对路径，并将反斜杠替换为正斜杠

parser = argparse.ArgumentParser() # 创建一个参数解析器对象
parser.add_argument('--input_dir', default='./resources/images/data/test/')  # training dataset # 添加一个参数，表示输入数据集的目录，默认为'./resources/images/data/test/'
parser.add_argument('--output_dir', default='./resources/images/data/test/')  # training dataset # 添加一个参数，表示输出数据集的目录，默认为'./resources/images/data/test/'
parser.add_argument('--para_dir', default='./parameters_densenet89/')  # training dataset # 添加一个参数，表示模型参数的目录，默认为'./parameters_densenet89/'
parser.add_argument('--b', type=int, default=1)  # batch size # 添加一个参数，表示批量大小，默认为1
parser.add_argument('--q', default='densenet89')  # save checkpoint parameters # 添加一个参数，表示基础模型的名称，默认为'densenet89'
opt = parser.parse_args() # 解析参数并赋值给opt对象
print(opt) # 打印opt对象

Net_Class_Set = 1 # 定义一个变量，表示需要转换的模型类型，0表示特征提取部分，1表示反卷积部分

Net_List = ['feature', 'deconv'] # 定义一个列表，存储模型类型的名称
Net_Input_List = [torch.rand(1, 3, 320, 240), torch.rand(1, 3, 192, 32, 32)] # 定义一个列表，存储模型类型对应的输入张量，随机生成
# 需要训练的模型类型地址，具体请参考说明文档
Net_Class = Net_List[Net_Class_Set] # 根据变量获取模型类型的名称
Net_Input = Net_Input_List[Net_Class_Set] # 根据变量获取模型类型对应的输入张量

# 实例化一个网络对象
if Net_Class_Set == 0: # 如果是特征提取部分
    model = getattr(densenet, opt.q)(pretrained=True).cpu() # 根据参数q获取densenet模型的特征提取部分，并加载预训练权重，并移动到CPU上
else: # 如果是反卷积部分
    model = Deconv(opt.q).cpu() # 创建一个Deconv类的实例，并移动到CPU上

Model_File_Path = Absolute_File_Path + "/model/{}_model.pth".format(Net_Class) # 定义模型参数文件的路径，根据绝对路径和模型类型名称拼接
Onnx_File_Path = Absolute_File_Path + "/model/{}_model.onnx".format(Net_Class) # 定义onnx文件的路径，根据绝对路径和模型类型名称拼接
model.load_state_dict(torch.load(Model_File_Path, map_location='cpu')) # 加载模型参数文件到模型中，并指定设备为CPU
model.eval() # 将模型设置为评估模式，不更新梯度和权重


def torch2onnx(model, save_path):
    """
    :param model:pkl 模型对象
    :param save_path:onnx onnx文件保存路径
    :return:onnx 将模型转换为onnx格式并保存到指定路径
    """
    model.eval() # 将模型设置为评估模式，不更新梯度和权重
    data = Net_Input # 获取输入张量
    input_names = ["{}_input".format(Net_Class)] # 定义输入张量的名称，根据模型类型名称拼接
    output_names = ["{}_out".format(Net_Class)] # 定义输出张量的名称，根据模型类型名称拼接
    torch.onnx._export(model, data, save_path, export_params=True, opset_version=11, input_names=input_names, output_names=output_names) # 将模型转换为onnx格式，并保存到指定路径，设置导出参数，版本号，输入输出名称等选项
    input("torch2onnx finish. 任意键退出...") # 等待用户输入任意键退出


if __name__ == '__main__':
    torch2onnx(model, Onnx_File_Path) # 调用torch2onnx函数，将模型转换为onnx格式
