import os
import cv2
import numpy as np
#im1 原图  im2 mask图(背景是黑色，前景是白色)
im1_path = 'input'
im2_path = 'outmask'

num = len(os.listdir(im1_path))
for i in range(num):

    img1 = cv2.imread(os.path.join(im1_path, os.listdir(im1_path)[i]))
    img2 = cv2.imread(os.path.join(im2_path,os.listdir(im2_path)[i]), cv2.IMREAD_GRAYSCALE)
    h,w,c = img1.shape
    img3 = np.zeros((h,w,4))
    img3[:,:,0:3] = img1
    img3[:,:,3] = img2
    #这里命名随意，但是要注意使用png格式
    cv2.imwrite('output/' + '%s' % os.listdir(im1_path)[i], img3)
