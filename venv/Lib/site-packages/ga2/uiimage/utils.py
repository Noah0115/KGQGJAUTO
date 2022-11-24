# -*- coding: UTF-8 -*-
import json
import numpy as np
import cv2


def _getPosition(img_query, img_scene, position):
    sceneImgH, sceneImgW = img_scene.shape[:2]
    queryImgH, queryImgW = img_query.shape[:2]
    expand = max(min(queryImgH, queryImgW), 60)
    if sceneImgH > sceneImgW:
        x_min = int(max(position[0] * sceneImgW - expand, 0))
        y_min = int(max(position[1] * sceneImgH - 1.5 * expand, 0))
        x_max = int(min(position[2] * sceneImgW + expand, sceneImgW))
        y_max = int(min(position[3] * sceneImgH + 1.5 * expand, sceneImgH))
    else:
        x_min = int(max(position[0] * sceneImgW - 1.5 * expand, 0))
        y_min = int(max(position[1] * sceneImgH - expand, 0))
        x_max = int(min(position[2] * sceneImgW + 1.5 * expand, sceneImgW))
        y_max = int(min(position[3] * sceneImgH + expand, sceneImgH))
    return (x_min, y_min, x_max, y_max)


def transparent(img_query, img_scene):
    h, w = img_query.shape[:2]
    img_query = cv2.GaussianBlur(img_query, (3, 3), 0)
    img_scene = cv2.GaussianBlur(img_scene, (3, 3), 0)
    binary_threshold = np.mean(img_query)
    img_scene_gray = cv2.cvtColor(img_scene, cv2.COLOR_BGR2GRAY)
    img_query_gray = cv2.cvtColor(img_query, cv2.COLOR_BGR2GRAY)
    retval, binary_scene = cv2.threshold(img_scene_gray, binary_threshold, 255, cv2.THRESH_BINARY)
    retval, binary_query = cv2.threshold(img_query_gray, binary_threshold, 255, cv2.THRESH_BINARY)
    # cv2.imshow('1', binary_query)
    # cv2.waitKey(0)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
    binary_query = cv2.erode(binary_query, kernel)
    binary_scene=cv2.erode(binary_scene,kernel)

    res = cv2.matchTemplate(binary_scene, binary_query, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)
    x_min = max_loc[0]
    y_min = max_loc[1]
    return max_val,(x_min,y_min,w,h)

def highlight(img_query, img_scene):
    img_query_hsv = cv2.cvtColor(img_query, cv2.COLOR_BGR2HSV)
    img_query_v =img_query_hsv[:, :, 2]
    img_query_v_mean = np.mean(img_query_v)
    img_scene_hsv = cv2.cvtColor(img_scene, cv2.COLOR_BGR2HSV)
    img_scene_v = img_scene_hsv[:, :, 2]
    img_scene_v_mean = np.mean(img_scene_v)
    if img_query_v_mean>img_scene_v_mean:
        return True
    else:
        return False

def highlightGraphic(img_query,img_scene,graphic='circle'):


    #find highlight Contours
    h, w = img_scene.shape[:2]
    img_scene_hsv = cv2.cvtColor(img_scene, cv2.COLOR_BGR2HSV)
    img_scene_v = img_scene_hsv[:, :, 2]
    max_v = np.max(img_scene_v)
    img_query_hsv = cv2.cvtColor(img_query, cv2.COLOR_BGR2HSV)
    img_query_v = img_query_hsv[:, :, 2]
    vThreshold = np.mean(img_query_v)
    _, binary = cv2.threshold(img_scene_v, vThreshold, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    binary = cv2.dilate(binary, kernel)
    contours_map, contours, hierarchy = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours_list = []
    rect_list = []
    arcL=0
    res_cnt=[]
    if len(contours) > 0:
        for i in range(len(contours)):
            cnt = contours[i]
            arcLength = cv2.arcLength(cnt, 1)
            area = cv2.contourArea(cnt)
            if graphic=="circle":
                if arcLength > 80 and area > 250:
                    x, y, w, h = cv2.boundingRect(cnt)
                    if w / h > 0.5 and w / h < 1.6:
                        contours_list.append(cnt)
                        rect_list.append((x, y, w, h))
            if graphic=="rectangle":
                if arcLength > 100:
                    if arcLength > arcL:
                        arcL = arcLength
                        res_cnt = cnt
    # rectangle
    if graphic == "rectangle":
        if res_cnt is None :
            return
        else:
            hull = cv2.convexHull(res_cnt)
            x, y, w, h = cv2.boundingRect(hull)
            # cv2.rectangle(img_scene, (x, y), (x + w, y + h), (0, 255, 0), 1)
            click_x = int(x + w / 2)
            click_y = int(y + h / 2)
            return (click_x, click_y)


    #circle
    if graphic=="circle":
        cnt_id = 0
        click_x = 0
        click_y = 0
        diff = 0.6
        if len(rect_list) > 0:
            for i in range(len(rect_list)):
                x, y, w, h = rect_list[i]
                if abs(w / h - 1) < diff:
                    diff = abs(w / h - 1)
                    cnt_id = i
            rect_x, rect_y, rect_w, rect_h = rect_list[cnt_id]

        circles = cv2.HoughCircles(binary, cv2.HOUGH_GRADIENT, 1, 100, param1=100, param2=30, minRadius=10,
                                   maxRadius=150)

        if circles is None:
            if rect_list:
                click_x = int(rect_x + rect_w / 2)
                click_y = int(rect_y + rect_h / 2)
                return (click_x, click_y)
            else:
                return
        else:
            circles_num = len(circles[0])
            if circles_num == 1:
                circle = circles[0]
                x = int(circle[0][0])
                y = int(circle[0][1])
                r = int(circle[0][2])
                return (x, y)
            elif circles_num > 1:
                res_tag = False

                for circle in circles[0]:
                    x = int(circle[0])
                    y = int(circle[1])
                    r = int(circle[2])

                    if x > rect_x and x < rect_x + rect_w and y > rect_y and y < rect_y + rect_h:
                        res_tag = True

                        return (x, y)
                if not res_tag:
                    return

def judge_SimpleColor(img_query):
    img_query=img_query[:,:,0]
    h, w = img_query.shape[:2]
    hist = cv2.calcHist([img_query], [0], None, [256], [0, 256])
    _, maxVal, _, maxLoc = cv2.minMaxLoc(hist)
    value=maxLoc[1]
    if value<200:
        return False
    else:
        count = 0
        for i in range(value - 5, min(value + 5, 256)):
            count += hist[i]
        percentage=count / h / w
        if percentage>0.6:
            return True
        else:
            return False


def specialBorder(img_scene):
    img_scene_temp0=img_scene[:,:,2].copy()
    img_scene_temp1=~img_scene_temp0
    h,w=img_scene_temp0.shape
    borderWidth=60
    topBorder = 0
    bottomBorder = 0
    leftBorder = 0
    rightBorder = 0
    if h>w:
        for i in range(h):
            if i<borderWidth:
                blackDetect0=np.count_nonzero(img_scene_temp0[i,:]>245)/len(img_scene_temp0[i,:])
                blackDetect1 = np.count_nonzero(img_scene_temp1[i, :] > 245)/len(img_scene_temp0[i,:])
                if blackDetect0>0.9 or blackDetect1>0.9 :
                    topBorder=topBorder+1
                    img_scene[i,:]=(0,0,255)
            if i > h - borderWidth:
                blackDetect0 = np.count_nonzero(img_scene_temp0[i, :] > 245) / len(img_scene_temp0[i, :])
                blackDetect1 = np.count_nonzero(img_scene_temp1[i, :] > 245) / len(img_scene_temp0[i, :])
                if blackDetect0 > 0.9 or blackDetect1 > 0.9:
                    bottomBorder = bottomBorder + 1
                    img_scene[i, :] = (0, 255, 0)


    else:
        for j in range(w):
            if j < borderWidth :
                blackDetect0 = np.count_nonzero(img_scene_temp0[:,j] > 245) / len(img_scene_temp0[:, j])
                blackDetect1 = np.count_nonzero(img_scene_temp1[:, j] > 245) / len(img_scene_temp0[:, j])
                if blackDetect0 > 0.9 or blackDetect1 > 0.9:
                    leftBorder = leftBorder + 1
                    img_scene[:,j] = (0, 0, 255)
            if j < borderWidth or j > w - borderWidth:
                blackDetect0 = np.count_nonzero(img_scene_temp0[:,j] > 245) / len(img_scene_temp0[:, j])
                blackDetect1 = np.count_nonzero(img_scene_temp1[:, j] > 245) / len(img_scene_temp0[:, j])
                if blackDetect0 > 0.9 or blackDetect1 > 0.9:
                    rightBorder = rightBorder + 1
                    img_scene[:,j] = (0, 255, 0)

    if topBorder>40 or bottomBorder>40 or leftBorder>40 or rightBorder>40:
        return True
    else:
        return False


class MatchResult(object):
    """
    匹配结果， 暂时包扩以下字段：
    - ``rect``: 模板位置， (left, top, right, bottom)
    - ``time``: 超找耗时
    - ``scale_ratio``: 得到结果的缩放比例
    - ``parameters``： 请求参数
    - ``miscellaneous``: 其它杂项, 字典类型
    类可以直接用作bool判断， 当rect为非None时返回True

    """
    __slots__ = ["method","rect", "time", "scale_ratio", "parameters", "miscellaneous"]

    def __init__(self, **kwargs):
        self.method=kwargs.get("method",None)
        self.rect = kwargs.get("rect", None)
        self.time = kwargs.get("time", -1)
        self.scale_ratio = kwargs.get("scale_ratio")
        self.parameters = kwargs.get("parameters", {})
        self.miscellaneous = kwargs.get("miscellaneous", {})

    def __bool__(self):
        return self.rect is None

    def __str__(self):
        d = {
            "method":self.method,
            "rect":self.rect,
            "time":self.time,
            "scale_ratio":self.scale_ratio,
            "parameters":self.parameters,
            "miscellaneous":self.miscellaneous
        }
        return json.dumps(d)
