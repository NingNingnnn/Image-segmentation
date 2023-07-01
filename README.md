本项目修改自:  
[Image-segmentation](https://github.com/NingNingnnn/Image-segmentation)  
在原先基础上实现了跨平台的CPU推理运行  
~~但是训练还是需要GPU,所以你可能得安装两个环境~~  
**强烈建议使用conda等虚拟环境进行配置**  
结构如下:
````
.
├── README.md
├── __pycache__
│   ├── dataset.cpython-311.pyc
│   ├── dataset.cpython-39.pyc
│   ├── densenet.cpython-311.pyc
│   ├── densenet.cpython-39.pyc
│   ├── model.cpython-311.pyc
│   └── model.cpython-39.pyc
├── chuli.py
├── chuli2.py
├── data.json
├── dataset.py
├── densenet.py
├── densenet121-a639ec97.pth
├── images
│   └── data
│       ├── test
│       │   ├── img
│       │   └── mask
│       └── train
│           ├── img
│           └── mask
├── initial.py
├── input
├── mask
├── mask.py
├── model.py
├── outmask
├── output
├── output.py
├── parameters_densenet121
│   ├── deconv_model.pth
│   └── feature_model.pth
├── requirements.txt
├── run.bat
├── run.command
├── test.py
├── tool_dataset2data.py
├── tool_img2data.py
├── tool_img2mask.py
├── tool_json2dataset.py
├── tool_torhc2onnx.py
├── train.py
├── ui3.11.py
└── ui3.12.py
````
# 项目介绍  
本项目是简单的基于FCN-Densenet的图像前后景分割项目  
macOS和Windows都可以运行
## 效果演示
4k3模型黑色背景抠图
![4k3原图](/sample/WechatIMG98.jpeg "4k3原图")
![4k3效果](/sample/WechatIMG99.png "4k3效果")
4k4模型黑色背景抠图  
![4k4原图](/sample/WechatIMG94.png "4k4原图")
![4k4mask](/sample/WechatIMG93.png "4k4mask")
![4k4效果](/sample/WechatIMG91.png "4k4效果")  
调整scale后  
![4k4调整mask](/sample/WechatIMG96.png "4k4调整mask")
![4k4调整效果](/sample/WechatIMG95.png "4k4调整效果")   
*调整scale可以改变二值化mask的阈值来改变消去强度*

# 快速开始
## 文件结构 
`input`  输入的待处理图像  
`output` 输出的文档  
`mask`   模型推理出的mask图  
`outmask`经过二值化的mask图
`parameters_densenet121`模型存放处(可自行替换)  
`data.json`内存放了处理参数,其中  
scale的值代表二值化处理时的强度(0-255)  
color代表输出是被扣去的部分所填充内容  
|white|black|none|
|:---:|:--:|:---:|
|白色|黑色|透明|  
  
  back代表是否反向mask  
|true|false|
|:---:|:--:|
|仅输出反向mask的结果|仅输出普通mask的结果| 



## 推理
### 选择模型
[模型下载地址](https://github.com/NingNingnnn/Image-segmentation/releases/tag/models)  
*下载解压后放到`parameters_densenet121`即可*
| 模型名称| 特性      |
|:--------:| :-------------:|
| 4k1 | 早期模型,不推荐 |
| 4k2 | 擅长单对象处理 |
| 4k3 | 擅长单对象前景,效果不错 |
| 4k4 | 擅长多对象前景扣除,推荐,且本仓库默认装载 |
| 4k5 | 擅长单对象前景,效果不错 |

### 配置环境
命令行内使用   
`pip install -r requirements.txt`  
~~requirements写的不太认真,如果有错误请自行解决~~
### 命令行
````
python initial.py
python test.py
python mask.py
python output.py
````
### 批处理
运行run.bat或run.command即可  
~~相信Linux用户不需要批处理~~
### GUI
运行`python ui3.12.py`即可

# 训练
## 数据集
将数据集分为原图和mask图分别放置在train和test文件夹中的img和mask文件夹中  
**请不要使用相同的数据**
## 训练
根据自己的数据集和自己的硬件设置参数后运行`train.py`  
在命令行中使用时可以从命令行中设置部分参数    
|--train_dir|--val_dir|--check_dir|
|:---:|:--:|:---:|
|training dataset|test dataset|save checkpoint parameters|  
|--q|--b|--e|
|save checkpoint parameters|batch size|epoches| 
|--svae_interval|
|svae interval|   
  
  ~~学习率自己手动改`train.py`去吧,所以其实上面的参数并没有什么卵用(反正都得改)~~