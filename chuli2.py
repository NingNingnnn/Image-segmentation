# 导入PIL库和os库
from PIL import Image
import os

# 获取"images"文件夹下的所有jpg图片的文件名
jpg_files = [f for f in os.listdir(r"D:\images") if f.endswith(".jpg")]
# 遍历所有jpg图片
for jpg_file in jpg_files:
    # 读取图片文件
    img = Image.open(os.path.join(r"", jpg_file))
    # 转换成RGB格式
    img_rgb = img.convert("RGB")
    # 获取图片文件名（不含扩展名）
    img_name = jpg_file.split(".")[0]
    # 生成保存路径和格式s
    save_path = os.path.join(r"D:\images", "rgb", img_name + ".png")
    # 保存RGB格式的png图片
    img_rgb.save(save_path)
