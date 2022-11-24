import os
import uiautomator2 as u2
import datetime
import time
import keyboard
import numpy as np
import cv2 as cv
d = u2.connect('127.0.0.1:62001')

def first():
    d.app_start('com.hypergryph.arknights')
    print('打开程序')
    print('等待10秒')
    time.sleep(20)
    d.click(0.496, 0.882) #点击进入
    print('进入界面1')
    print('等待10秒')
    time.sleep(10)
    d.click(0.512, 0.701)  # 点击进入
    print('进入主界面')
    time.sleep(15)
def LS4(count):
    print('进入终端')
    d.click(0.758, 0.229)   #打开终端
    time.sleep(3)
    print('进入资源收集')
    d.click(0.56, 0.932)    #资源收集
    print('进入战术演习')
    time.sleep(1)
    d.click(0.506, 0.537)   #战术演习
    time.sleep(1)
    d.click(0.701, 0.556)   #LS-4
    time.sleep(1)
    d.click(0.899, 0.934)   #开始行动1
    time.sleep(3)
    d.click(0.861, 0.72)    #开始行动2
    print('开始关卡，等待时间90秒')
    time.sleep(90)
    d.click(0.861, 0.72)  # 结束
    time.sleep(5)
    for i in range(0, count-1):
        d.click(0.886, 0.946)  # 开始行动
        time.sleep(3)
        d.click(0.861, 0.72)  # 开始行动2
        print('开始关卡，等待时间90秒')
        time.sleep(90)
        d.click(0.861, 0.72)  # 结束
        time.sleep(5)
if __name__ == '__main__':
    first()
    LS4(2)