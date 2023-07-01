import os
import numpy as np
import PIL.Image as Image
import torch
from torch.utils import data
import random
import scipy.stats
import cv2


class MySynData(data.Dataset):
    """
    synthesis data
    这是一个自定义的数据集类，用于生成合成的图像和掩码
    """
    mean = np.array([0.485, 0.456, 0.406])# 定义图像的均值
    std = np.array([0.229, 0.224, 0.225])# 定义图像的标准差

    def __init__(self, obj_root, bg_root, transform=True, hflip=False, vflip=False, crop=False):
        """
        初始化数据集类的属性
        obj_root: 对象图片的根目录
        bg_root: 背景图片的根目录
        transform: 是否对图像进行转换
        hflip: 是否对图像进行水平翻转
        vflip: 是否对图像进行垂直翻转
        crop: 是否对图像进行裁剪
        """        
        super(MySynData, self).__init__()
        self.obj_root, self.bg_root = obj_root, bg_root# 定义对象和背景的根目录
        self.is_transform = transform# 是否对图像进行转换
        self.is_hflip = hflip# 是否对图像进行水平翻转
        self.is_vflip = vflip# 是否对图像进行垂直翻转
        self.is_crop = crop# 是否对图像进行裁剪
        obj_names = os.listdir(obj_root)# 获取对象目录下的所有文件名
        bg_names = os.listdir(bg_root)# 获取背景目录下的所有文件名
        self.name_combs = [(obj_name, bg_name) for obj_name in obj_names for bg_name in bg_names]# 生成对象和背景的所有组合

    def __len__(self):
        """
        返回数据集的长度，即组合的数量
        """
        return len(self.name_combs)# 返回数据集的长度，即组合的数量

    def __getitem__(self, index):
        """
        根据索引返回一个合成的图像和掩码
        index: 索引值，范围从0到数据集长度减1
        """
        obj_name, bg_name = self.name_combs[index]# 根据索引获取对象和背景的文件名
        obj = Image.open('%s/%s' % (self.obj_root, obj_name))# 打开对象图片

        bg = Image.open('%s/%s' % (self.bg_root, bg_name))# 打开背景图片
        sbc, sbr = bg.size# 获取背景图片的宽度和高
        ratio = 400.0 / max(sbr, sbc)
        bg = bg.resize((int(sbc * ratio), int(sbr * ratio)))
        bg = np.array(bg, dtype=np.uint8)

        r, c, _ = bg.shape
        r_location = scipy.stats.weibull_min.rvs(1.56, 0, 0.22, size=1)[0] * r
        r_location = int(r_location)
        r_location = min(r_location, r-1)
        c_location = scipy.stats.weibull_min.rvs(1.72, 0, 0.27, size=1)[0] * c
        c_location = int(c_location)
        c_location = min(c_location, c-1)
        length = scipy.stats.norm.rvs(0.61, 0.07, size=1)[0] * max(r, c)
        length = max(length, 10)

        sbc, sbr = obj.size
        ratio = length / max(sbr, sbc)
        obj = obj.resize((int(sbc * ratio), int(sbr * ratio)))
        sbc, sbr = obj.size

        r_location_end = min(r_location + sbr, r)
        c_location_end = min(c_location + sbc, c)

        obj_r_end = min(r_location_end - r_location, sbr)
        obj_c_end = min(c_location_end - c_location, sbc)

        obj = np.array(obj, dtype=np.uint8)
        m_obj = obj[:, :, 3]
        m_obj[m_obj != 0] = 1
        m_obj = np.expand_dims(m_obj, 2)
        obj = obj[:, :, :3]

        mask = np.zeros((bg.shape[0], bg.shape[1], 1))

        bg[r_location:r_location_end, c_location:c_location_end] = \
            bg[r_location:r_location_end, c_location:c_location_end] * (1 - m_obj[:obj_r_end, :obj_c_end]) \
            + obj[:obj_r_end, :obj_c_end] * m_obj[:obj_r_end, :obj_c_end]
        mask[r_location:r_location_end, c_location:c_location_end] = \
            m_obj[:obj_r_end, :obj_c_end]

        bg = bg.astype(np.uint8)
        mask = mask.astype(np.uint8)
        mask[mask != 0] = 1

        if self.is_crop:
            H = int(0.9 * bg.shape[0])
            W = int(0.9 * bg.shape[1])
            H_offset = random.choice(range(bg.shape[0] - H))
            W_offset = random.choice(range(bg.shape[1] - W))
            H_slice = slice(H_offset, H_offset + H)
            W_slice = slice(W_offset, W_offset + W)
            bg = bg[H_slice, W_slice, :]
            mask = mask[H_slice, W_slice]
        if self.is_hflip and random.randint(0, 1):
            bg = bg[:, ::-1, :]
            mask = mask[:, ::-1]
        if self.is_vflip and random.randint(0, 1):
            bg = bg[::-1, :, :]
            mask = mask[::-1, :]
        bg = cv2.resize(bg, dsize=(256, 256), interpolation=cv2.INTER_NEAREST)
        mask = cv2.resize(mask, dsize=(256, 256), interpolation=cv2.INTER_NEAREST)

        if self.is_transform:
            bg, mask = self.transform(bg, mask)
            return bg, mask
        else:
            return bg, mask

    def transform(self, img, gt):
        img = img.astype(np.float64) / 255
        img -= self.mean
        img /= self.std
        img = img.transpose(2, 0, 1)
        img = torch.from_numpy(img).float()

        gt = torch.from_numpy(gt)
        return img, gt


class MyData(data.Dataset):
    """
    load images for testing
    root: director/to/images/
            structure:
            - root
                - images (images here)
                - masks (ground truth)
    """
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])

    def __init__(self, root, transform=True, hflip=False, vflip=False, crop=False):
        super(MyData, self).__init__()
        self.root = root
        self.is_transform = transform
        self.is_hflip = hflip
        self.is_vflip = vflip
        self.is_crop = crop
        img_root = os.path.join(self.root, 'img')
        gt_root = os.path.join(self.root, 'mask')
        file_names = os.listdir(gt_root)
        self.img_names = []
        self.map_names = []
        self.gt_names = []
        self.names = []
        for i, name in enumerate(file_names):
            if not name.endswith('.png'):
                continue
            self.img_names.append(img_root + '\\' + name[:-4] + '.png')
            self.gt_names.append(gt_root + '\\' + name[:-4] + '.png')
            self.names.append(name[:-4])

    def __len__(self):
        return len(self.gt_names)

    def __getitem__(self, index):
        # load image
        img_file = self.img_names[index]
        img = Image.open(img_file)
        img = np.array(img, dtype=np.uint8)
        if len(img.shape) < 3:
            img = np.stack((img, img, img), 2)
        if img.shape[2] > 3:
            img = img[:, :, :3]

        gt_file = self.gt_names[index]
        gt = Image.open(gt_file)
        gt = np.array(gt, dtype=np.int32)
        gt[gt != 0] = 1
        if self.is_crop:
            H = int(0.9 * img.shape[0])
            W = int(0.9 * img.shape[1])
            H_offset = random.choice(range(img.shape[0] - H))
            W_offset = random.choice(range(img.shape[1] - W))
            H_slice = slice(H_offset, H_offset + H)
            W_slice = slice(W_offset, W_offset + W)
            img = img[H_slice, W_slice, :]
            gt = gt[H_slice, W_slice]
        if self.is_hflip and random.randint(0, 1):
            img = img[:, ::-1, :]
            gt = gt[:, ::-1]
        if self.is_vflip and random.randint(0, 1):
            img = img[::-1, :, :]
            gt = gt[::-1, :]
        img = cv2.resize(img, dsize=(256, 256), interpolation=cv2.INTER_NEAREST)
        gt = cv2.resize(gt, dsize=(256, 256), interpolation=cv2.INTER_NEAREST)

        if self.is_transform:
            img, gt = self.transform(img, gt)
            return img, gt
        else:
            return img, gt

    def transform(self, img, gt):
        img = img.astype(np.float64) / 255
        img -= self.mean
        img /= self.std
        img = img.transpose(2, 0, 1)
        img = torch.from_numpy(img).float()

        gt = torch.from_numpy(gt)
        return img, gt


class MyTestData(data.Dataset):
    """
    load images for testing
    root: director/to/images/
            structure:
            - root
                - images (images here)
                - masks (ground truth)
    这是一个自定义的数据集类，用于加载测试用的图像和掩码
    """
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])

    def __init__(self, root, transform=True):
        """
        初始化数据集类的属性
        root: 图像和掩码的根目录
        transform: 是否对图像进行转换
        """
        super(MyTestData, self).__init__()
        self.root = root
        self._transform = transform

        img_root = os.path.join(self.root)
        file_names = os.listdir(img_root)
        self.img_names = []
        self.names = []
        for i, name in enumerate(file_names):
            if not name.endswith('.png'):
                continue
            self.img_names.append(img_root + '/' + name[:-4] + '.png')
            self.names.append(name[:-4])

    def __len__(self):
        """
        返回数据集的长度，即图像文件名列表的长度
        """
        return len(self.img_names)

    def __getitem__(self, index):
        """
        根据索引返回一个图像和掩码
        index: 索引值，范围从0到数据集长度减1
        """
        # load image
        img_file = self.img_names[index]
        img = Image.open(img_file)
        img_size = img.size
        img = img.resize((256, 256))
        img = np.array(img, dtype=np.uint8)
        if self._transform:
            img = self.transform(img)
            return img, self.names[index], img_size
        else:
            return img, self.names[index], img_size

    def transform(self, img):
        """
        对图像进行转换，包括归一化，减去均值，除以标准差，转置维度，转换为torch张量等操作
        img: numpy数组类型的图像数据
        """
        img = img.astype(np.float64) / 255
        img -= self.mean
        img /= self.std
        img = img.transpose(2, 0, 1)
        img = torch.from_numpy(img).float()
        return img
