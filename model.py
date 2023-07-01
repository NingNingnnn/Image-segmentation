import torch.nn as nn


def nothing(x):
    return x # 定义一个空函数，用于不需要降维的情况


dim_dict = {
    'resnet101': [512, 1024, 2048],
    'resnet152': [512, 1024, 2048],
    'resnet50': [512, 1024, 2048],
    'resnet34': [128, 256, 512],
    'resnet18': [128, 256, 512],
    'densenet57': [144, 200, 456],
    'densenet89': [192, 352, 736],
    'densenet121': [256, 512, 1024],
    'densenet161': [384, 1056, 2208],
    'densenet169': [256, 640, 1664],
    'densenet201': [256, 896, 1920]
} # 定义一个字典，存储不同的基础模型的特征维度


class Deconv(nn.Module):
    """
    定义一个反卷积类，用于对特征进行上采样和融合，生成掩码输出
    base: 基础模型的名称，默认为'vgg'
    """
    def __init__(self, base='vgg'):
        super(Deconv, self).__init__()
        if base == 'vgg':
            self.pred5 = nn.Sequential(
                nn.Conv2d(512, 1, kernel_size=1), # 对第五层特征进行1x1卷积，将通道数降为1
                nn.ReLU() # 使用ReLU激活函数
            )
            self.reduce_channels = [nothing, nothing, nothing] # 对于vgg模型，不需要降维操作，所以使用空函数列表
        else:
            self.pred5 = nn.Sequential(
                nn.Conv2d(512, 1, kernel_size=1), # 对第五层特征进行1x1卷积，将通道数降为1
                nn.ReLU(), # 使用ReLU激活函数
                nn.UpsamplingBilinear2d(scale_factor=2) # 使用双线性插值法进行上采样，放大两倍
            )
            self.reduce_channels = nn.ModuleList([
                nn.Conv2d(in_dim, out_dim, kernel_size=1) for in_dim, out_dim in zip(dim_dict[base], [256, 512, 512])
            ]) # 对于其他模型，需要使用1x1卷积进行降维操作，根据基础模型的名称从字典中获取输入和输出的维度，并创建一个模块列表
        self.pred4 = nn.Sequential(
            nn.Conv2d(512, 1, kernel_size=1), # 对第四层特征进行1x1卷积，将通道数降为1
            nn.ReLU(), # 使用ReLU激活函数
            nn.UpsamplingBilinear2d(scale_factor=2) # 使用双线性插值法进行上采样，放大两倍
        )
        self.pred3 = nn.Sequential(
            nn.Conv2d(256, 1, kernel_size=1), # 对第三层特征进行1x1卷积，将通道数降为1
            nn.UpsamplingBilinear2d(scale_factor=8) # 使用双线性插值法进行上采样，放大八倍
        )
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                m.weight.data.normal_(0, 0.01) # 初始化卷积层的权重为正态分布，均值为0，标准差为0.01
                m.bias.data.fill_(0) # 初始化卷积层的偏置为0

    def forward(self, x):
        """
        前向传播函数，对输入的特征进行反卷积操作，生成掩码输出
        x: 输入的特征列表，包含三个元素，分别对应第三层，第四层，第五层的特征
        """
        x = [r(_x) for r, _x in zip(self.reduce_channels, x)] # 对每个特征进行降维操作，如果不需要降维，则使用空函数
        pred5 = self.pred5(x[2]) # 对第五层特征进行反卷积操作，得到第五层的预测输出
        pred4 = self.pred4(pred5 + x[1]) # 将第五层的预测输出和第四层的特征相加，再进行反卷积操作，得到第四层的预测输出
        pred3 = self.pred3(pred4 + x[0]) # 将第四层的预测输出和第三层的特征相加，再进行反卷积操作，得到第三层的预测输出
        return pred3 # 返回最终的预测输出
