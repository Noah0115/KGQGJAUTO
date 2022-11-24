import os

import keyboard
import uiautomator2 as u2
import datetime
import time
import numpy as np
import cv2 as cv


####################
RoiX1 = -1
RoiY1 = -1
RoiX2 = -1
RoiY2 = -1
MouseDownFlag = False
Canvas = cv.imdecode(np.zeros(1, np.uint8), cv.IMREAD_COLOR)
TempCanvas = Canvas
########################



def mouse_event(event, x, y, flags, param):
    global RoiX1, RoiY1, RoiX2, RoiY2, Canvas, TempCanvas, MouseDownFlag
    if event == cv.EVENT_LBUTTONDOWN:
        MouseDownFlag = True
        RoiX1 = x
        RoiY1 = y
        Canvas = param.copy()
        putText = "(%d,%d)" % (RoiX1, RoiY1)  # 设置坐标显示格式
        cv.circle(Canvas, (RoiX1, RoiY1), 2, (0, 255, 0), thickness=-1)
        cv.putText(Canvas, putText, (RoiX1 + 10, RoiY1 - 10), cv.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), thickness=1)
        TempCanvas = Canvas.copy()
    elif event == cv.EVENT_MOUSEMOVE:
        if not MouseDownFlag:
            return
        RoiX2 = x
        RoiY2 = y
        dx = RoiX2 - RoiX1
        dy = RoiY2 - RoiY1
        if dx > 0 and dy > 0:
            Canvas = TempCanvas.copy()  # 消除重影
            cv.rectangle(Canvas, (RoiX1, RoiY1), (RoiX2, RoiY2), (0, 0, 255), 1)
    elif event == cv.EVENT_LBUTTONUP:
        RoiX2 = x
        RoiY2 = y
        putText = "(%d,%d)" % (RoiX2, RoiY2)  # 设置坐标显示格式
        cv.circle(Canvas, (RoiX2, RoiY2), 2, (0, 255, 0), thickness=-1)
        cv.putText(Canvas, putText, (RoiX2 - 15, RoiY2 + 15), cv.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), thickness=1)
        MouseDownFlag = False


def draw_roi(devices):
    global Canvas
    while True:
        targetImg = devices.screenshot(format='opencv')
        cv.namedWindow("Please check the required area (y: confirm the check, n: Re-cutting, esc:quit)",
                       cv.WINDOW_AUTOSIZE)
        cv.setMouseCallback("Please check the required area (y: confirm the check, n: Re-cutting, esc:quit)",
                            mouse_event, targetImg)
        Canvas = targetImg.copy()
        flag = False
        while True:
            cv.imshow("Please check the required area (y: confirm the check, n: Re-cutting, esc:quit)", Canvas)
            cv.waitKey(1)
            if keyboard.is_pressed('y'):
                cv.destroyAllWindows()
                print("(%d,%d),(%d,%d)" % (RoiX1, RoiY1, RoiX2, RoiY2))
                if RoiX1 < 0 or RoiY1 < 0 or RoiX2 < 0 or RoiY2 < 0:
                    print("截取错误，重新截取")
                    flag = True
                    break
                roiImg = targetImg[RoiY1:RoiY2, RoiX1:RoiX2]
                cv.namedWindow("Image", cv.WINDOW_AUTOSIZE)
                cv.imshow("Image", roiImg)
                cv.waitKey(1)
                img_name = input("请输入保存的图像名称(默认格式jpg):\n")
                cv.imwrite("./pictemplate/" + img_name + ".jpg", roiImg)
                cv.destroyAllWindows()
                print("图像已保存!")
                flag = True
                break
            elif keyboard.is_pressed('n'):
                cv.destroyAllWindows()
                print("重新裁剪")
                flag = True
                break
            elif keyboard.is_pressed('esc'):
                break
        if not flag:
            break


if __name__ == '__main__':
    os.system("adb connect 127.0.0.1:62001")
    d = u2.connect("127.0.0.1:62001")  # USB控制设备端口号
    draw_roi(d)
    print("裁剪完成")
