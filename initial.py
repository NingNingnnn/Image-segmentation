import os
file_path = "input" # 你想要检查或创建的文件夹路径
if not os.path.exists(file_path): # 如果文件夹不存在
    os.makedirs(file_path) # 创建文件夹
file_path = "output" # 你想要检查或创建的文件夹路径
if not os.path.exists(file_path): # 如果文件夹不存在
    os.makedirs(file_path) # 创建文件夹
file_path = "mask" # 你想要检查或创建的文件夹路径
if not os.path.exists(file_path): # 如果文件夹不存在
    os.makedirs(file_path) # 创建文件夹
file_path = "outmask" # 你想要检查或创建的文件夹路径
if not os.path.exists(file_path): # 如果文件夹不存在
    os.makedirs(file_path) # 创建文件夹
folder_path = 'mask'
file_list = os.listdir(folder_path)
for file_name in file_list:
    file_path = os.path.join(folder_path, file_name)
    os.remove(file_path)
folder_path = 'outmask'
file_list = os.listdir(folder_path)
for file_name in file_list:
    file_path = os.path.join(folder_path, file_name)
    os.remove(file_path)