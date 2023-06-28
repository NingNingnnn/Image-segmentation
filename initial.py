import os
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