import os
import keyboard
import uiautomator2 as u2
import datetime
import time
import numpy as np
import cv2 as cv

d = u2.connect('127.0.0.1:62001')

def stepone():
    d.app_start('com.bilibili.snake')
    print('打开程序')
    time.sleep(7)
    d.click(0.496, 0.882)  # 点击进入
    time.sleep(3)
    d.click(0.496, 0.882)  # 点击进入
    time.sleep(3)
    d.click(0.496, 0.882)  # 点击进入
    print('进入界面1')
    time.sleep(3)
    d.click(0.496, 0.882)  # 点击进入
    print('等待10秒')
    time.sleep(15)
    d.click(0.512, 0.701)  # 点击进入
    d.click(0.512, 0.701)  # 点击进入
    print('进入主界面')
    time.sleep(23)


def testpic(filename,uiname):
    # 读取货物图片
    template = cv.imread('./pictemplate/'+filename)
    # 获取货物图片的长宽信息
    th, tw = template.shape[:2]
    Flag = True
    min_loc = 0
    global screen
    while Flag:
        # stepone()
        d.screenshot('./screen/' + uiname + '.jpg', format='opencv')
        screen = cv.imread('./screen/' + uiname + '.jpg')
        # 调用 OpenCV 的模版匹配方法
        res = cv.matchTemplate(screen, template, cv.TM_SQDIFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
        if min_val <= 0.15:
            print('找到了，已截图到根目录下Result.jpg', min_val)
            Flag = False
        else:
            print('没找到，继续找', min_val)
    # min_val 可用来判断是否检测到货物
    # 矩形左上角坐标
    tl = min_loc
    # 矩形右下角坐标
    br = (tl[0] + tw, tl[1] + th)
    cv.rectangle(screen, tl, br, (0, 0, 255), 2)
    cv.imwrite('Result.jpg', screen)


if __name__ == '__main__':
    h1 = 'happy2500.jpg'
    h2 = 'happy2500'
    testpic(h1,h2)
