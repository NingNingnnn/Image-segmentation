import cv2
import os
import json
with open("data.json", "r") as f: # 打开json文件
    data = json.load(f) # 读取并解码json数据

# 获取图片文件夹的路径
input_path = "mask"
# 获取输出文件夹的路径
output_path = "outmask"

# 遍历图片文件夹中的所有文件
for file in os.listdir(input_path):
    # 拼接完整的文件路径
    file_path = os.path.join(input_path, file)
    # 判断是否是图片文件
    if file_path.endswith(".png") or file_path.endswith(".jpg"):
        # 读取图片文件
        im = cv2.imread(file_path)
        # 转换成灰度图像
        im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        # 根据阈值进行二值化，这里假设阈值是128，你可以根据需要修改
        _, im = cv2.threshold(im, int(data["scale"]), 255, cv2.THRESH_BINARY)
        # 拼接输出文件的路径
        output_file_path = os.path.join(output_path, file)
        # 保存图片文件
        cv2.imwrite(output_file_path, im)