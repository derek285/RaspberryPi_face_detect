from PIL import Image
import cv2
import numpy as np

def hash_img(img):
    a = []
    hash_img = ''
    width,height = 10,10
    img = img.resize((width,height))
    for y in range(img.height):
        b = []
        for x in range(img.width):
            pos = x,y
            color_array = img.getpixel(pos)
            color = sum(color_array)/3
            b.append(int(color))
        a.append(b)
    for y in range(img.height):
        avg = sum(a[y]) / len(a[y])
        for x in range(img.width):
            if a[y][x] >= avg:
                hash_img += '1'
            else:
                hash_img += '0'
                
    return hash_img
    
def similar(img1, img2):
    hash1 = hash_img(img1)
    hash2 = hash_img(img2)
    differnce = 0
    for i in range(len(hash1)):
        differnce += abs(int(hash1[i]) - int(hash2[i]))
    similar = 1 - (differnce/len(hash1))
    return similar

pil_immg = Image.open('face.png')
# convert from cv.imread, same
cv_img = cv2.imread('face.png')
pil_img = Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))
# pil_img = np.asarray(pil_img)
# cv2.imshow('cv_img', cv_img)
# cv2.waitKey(0)
# cv2.imshow('pil_img', pil_img)
# cv2.waitKey(0)

img2 = Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))
print(similar(pil_img, img2) * 100)