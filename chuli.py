# 导入所需的库
import cv2
import os
from PIL import Image

# 定义文件夹路径，您可以根据需要修改
folder_path = "D:\\projects\\github\\source\\images\\data\\train\\img"

# 遍历文件夹中的所有png文件
for file in os.listdir (folder_path):
    if file.endswith (".png"):
        # 获取文件的完整路径
        file_path = os.path.join (folder_path, file)
        # 读取图像为numpy数组
        img = cv2.imread (file_path)
        # 检查图像的通道数，如果不是3，则进行转换
        if img.shape [2] != 3:
            # 使用OpenCV的cvtColor函数将图像转换为3通道BGR格式
            img = cv2.cvtColor (img, cv2.COLOR_BGRA2BGR)
            # 或者使用PIL的convert函数将图像转换为3通道RGB格式
            # img = Image.open (file_path)
            # img = img.convert ("RGB")
            # img = np.array (img)
        # 保存转换后的图像到原路径，覆盖原文件
        cv2.imwrite (file_path, img)
