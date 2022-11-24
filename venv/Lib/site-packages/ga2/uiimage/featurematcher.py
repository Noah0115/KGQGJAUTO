#-*- coding: UTF-8 -*-
import os
import cv2
import time
import logging
import datetime
import numpy as np
from .utils import MatchResult,_getPosition,transparent,judge_SimpleColor,highlight,specialBorder

from . import cv2helper
from .tmplatematcher import TemplateMatcher

logger = logging.getLogger('cvmatcher')
logger.setLevel(logging.INFO)
_filter = logging.Filter(name='cvmatcher')


class FeatureMatcher(object):
    # SIFT参数: FILTER_RATIO为SIFT优秀特征点过滤比例值(0-1范围,建议值0.4-0.6)
    filter_ratio = 0.59
    # SIFT参数: SIFT识别时只找出一对相似特征点时的置信度(confidence)
    one_point_confidence = 0.8


    def _init(self, name):
        # self.result = MatchResult()

        FLANN_INDEX_KDTREE = 1  # bug: flann enums are missing
        FLANN_INDEX_LSH = 6
        chunks = name.split('-')
        norm = None
        # Make sure that there is SIFT module in OpenCV.
        if cv2.__version__.startswith("3."):
            # OpenCV3.x, sift is in contrib module, you need to compile it seperately.
            if chunks[0] == 'sift':
                try:
                    detector = cv2helper.eval2('cv2.xfeatures2d.SIFT_create')(edgeThreshold=10)
                    norm = cv2helper.eval2('cv2.NORM_L2')
                except:
                    print("to use SIFT, you should build contrib with opencv3.0")
                    logger.error("There is no SIFT module in your OpenCV environment !")
            elif chunks[0] == 'surf':
                try:
                    detector = cv2helper.eval2('cv2.xfeatures2d.SURF_create')(800)
                    norm = cv2helper.eval2('cv2.NORM_L2')
                except:
                    print("to useSURF, you should build contrib with opencv3.0")
                    logger.error("There is no SURF module in your OpenCV environment !")
            elif chunks[0] == 'orb':
                try:
                    detector = cv2helper.eval2('cv2.ORB_create')(400)
                    norm = cv2helper.eval2('cv2.NORM_HAMMING')
                except:
                    print("to useORB, you should build contrib with opencv3.0")
                    logger.error("There is no ORB module in your OpenCV environment !")
            else:
                raise ValueError('unknown detector:%s' % name)
        
        else:
            # OpenCV2.x, just use it.
            if chunks[0] == 'sift':
                detector = cv2helper.eval2('cv2.SIFT')(edgeThreshold=10)
                norm = cv2helper.eval2('cv2.NORM_L2')
            elif chunks[0] == 'surf':
                detector = cv2helper.eval2('cv2.SURF')(800)
                norm = cv2helper.eval2('cv2.NORM_L2')
            elif chunks[0] == 'orb':
                detector = cv2helper.eval2('cv2.ORB')(400)
                norm = cv2helper.eval2('cv2.NORM_HAMMING')
            else:
                raise ValueError('unknown detector:%s' % name)
        if norm is None:
            return None, None
        
        if 'flann' in chunks:
            if norm == cv2helper.eval2('cv2.NORM_L2'):
                flann_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
            else:
                flann_params = dict(algorithm=FLANN_INDEX_LSH,
                                    table_number=6,  # 12
                                    key_size=12,  # 20
                                    multi_probe_level=1)  # 2
            matcher = cv2helper.eval2('cv2.FlannBasedMatcher')(flann_params,
                                                               {})  # bug : need to pass empty dict (#1329)
        else:
            matcher = cv2helper.eval2('cv2.BFMatcher')(norm)
        return detector, matcher

    def _getImageData(self, filePath, gray):
        if not os.path.exists(filePath):
            logger.error('file not found:%s' % filePath)
            return None

        imgData = cv2helper.imread(filePath)
        if imgData is None:
            logger.error('invalid image format!')
            return None

        channel = imgData.shape[2]
        if not gray or (channel == 1 and gray):
            return imgData

        imgData = cv2helper.cvtColor(imgData)
        if imgData is None:
            logger.error('failed to covert to gray image')
            return None

        return imgData


    def _getKeyPoints(self, detector,imageData, method='sift-flann'):
        keyPoints, desc = detector.detectAndCompute(imageData, None)
        return keyPoints, desc

    def _filterMatchedPoints(self, kp_scene, desc_scene, kp_query, desc_query, matcher, good_ratio, queryImageWidth):
        # if len(kp_scene) < 2 or len(kp_query) < 2:
        ## logger.error("Not enough feature points in input images !")
        # 匹配两个图片中的特征点集,k=2表示每个特征点取出2个最匹配的对应点:
        # if len(kp_scene) >= 2 and len(kp_query) >= 2:
        matches = matcher.knnMatch(desc_query, desc_scene, k=2)

        # print('matches',len(matches))
        good = []
        # good为特征点初选结果,剔除掉前两名匹配太接近的特征点,不是独特优秀的特征点直接筛除(多目标识别情况直接不适用)
        for m, n in matches:
            if m.distance < good_ratio * n.distance:
                good.append(m)


        # good点需要去除重复的部分,（设定源图像不能有重复点）去重时将src图像中的重复点找出即可
        # 去重策略：允许搜索图像对源图像的特征点映射一对多,不允许多对一重复（即不能源图像上一个点对应搜索图像的多个点）
        good_diff, diff_good_point = [], [[]]
        if good:
            for m in good:

                diff_point = [int(kp_scene[m.trainIdx].pt[0]), int(kp_scene[m.trainIdx].pt[1])]

                if diff_point not in diff_good_point:
                    good_diff.append(m)
                    diff_good_point.append(diff_point)

            good = good_diff

        if good:
            # 根据匹配斜率一致原则去除误匹配点
            k = []
            good_temp = good[:]
            for p in good:
                p_query = kp_query[p.queryIdx].pt
                p_scene = kp_scene[p.trainIdx].pt

                k.append((p_scene[1] - p_query[1]) / (queryImageWidth + p_scene[0] - p_query[0]))

            m_k = np.median(k)
            logger.debug('k in KeyPoints filter is :%s' % m_k)
            for i in range(len(good_temp)):
                if abs(k[i] - m_k) > 0.1:
                    good.remove(good_temp[i])
            del good_temp

        return kp_query, kp_scene, good


    def generate_result(self, middle_point, pypts, confi):
        """
        Format the result: 定义图像识别结果格式
        """
        rect = dict(result=middle_point,
                    rectangle=pypts,
                    confidence=confi)
        return rect

    def _handle_onePoints(self, img_scene, img_query, kp_scene, kp_query, good):
        """sift匹配中只有一对匹配的特征点对的情况."""
        # 识别中心即为该匹配点位置
        pts_query = int(kp_query[good[0].queryIdx].pt[0]), int(kp_query[good[0].queryIdx].pt[1])
        pts_scene = int(kp_scene[good[0].trainIdx].pt[0]), int(kp_scene[good[0].trainIdx].pt[1])
        return self._onePoints(pts_query, pts_scene, img_scene, img_query)

    def _handle_twoPoints(self, img_scene, img_query, kp_scene, kp_query, good):
        """处理两对特征点的情况."""

        pts_query1 = int(kp_query[good[0].queryIdx].pt[0]), int(kp_query[good[0].queryIdx].pt[1])
        pts_query2 = int(kp_query[good[1].queryIdx].pt[0]), int(kp_query[good[1].queryIdx].pt[1])
        pts_scene1 = int(kp_scene[good[0].trainIdx].pt[0]), int(kp_scene[good[0].trainIdx].pt[1])
        pts_scene2 = int(kp_scene[good[1].trainIdx].pt[0]), int(kp_scene[good[1].trainIdx].pt[1])

        return self._twoPoints(pts_query1, pts_query2, pts_scene1, pts_scene2, img_scene, img_query)

    def _handle_threePoints(self, img_scene, img_query, kp_scene, kp_query, good):
        """处理三对特征点的情况."""
        # 拿出query和scene的两个点(点1)和(点2点3的中点),
        # 然后根据两个点原则进行后处理(注意ke_query和kp_scene以及queryIdx和trainIdx):
        pts_query1 = int(kp_query[good[0].queryIdx].pt[0]), int(kp_query[good[0].queryIdx].pt[1])
        pts_query2 = int((kp_query[good[1].queryIdx].pt[0] + kp_query[good[2].queryIdx].pt[0]) / 2), int(
            (kp_query[good[1].queryIdx].pt[1] + kp_query[good[2].queryIdx].pt[1]) / 2)
        pts_scene1 = int(kp_scene[good[0].trainIdx].pt[0]), int(kp_scene[good[0].trainIdx].pt[1])
        pts_scene2 = int((kp_scene[good[1].trainIdx].pt[0] + kp_scene[good[2].trainIdx].pt[0]) / 2), int(
            (kp_scene[good[1].trainIdx].pt[1] + kp_scene[good[2].trainIdx].pt[1]) / 2)

        return self._twoPoints(pts_query1, pts_query2, pts_scene1, pts_scene2, img_scene, img_query)

    def _handle_manyPoints(self, img_scene, img_query, kp_scene, kp_query, good):

        num = len(good)
        pts_query_x = []
        pts_query_y = []
        pts_scene_x = []
        pts_scene_y = []
        for p in range(num):
            pts_query_x.append(kp_query[good[p].queryIdx].pt[0])
            pts_query_y.append(kp_query[good[p].queryIdx].pt[1])
            pts_scene_x.append(kp_scene[good[p].trainIdx].pt[0])
            pts_scene_y.append(kp_scene[good[p].trainIdx].pt[1])
        pts_query1 = int(np.min(pts_query_x)), int(np.min(pts_query_y))
        pts_query2 = int(np.max(pts_query_x)), int(np.max(pts_query_y))
        pts_scene1 = int(np.min(pts_scene_x)), int(np.min(pts_scene_y))
        pts_scene2 = int(np.max(pts_scene_x)), int(np.max(pts_scene_y))

        return self._twoPoints(pts_query1, pts_query2, pts_scene1, pts_scene2, img_scene, img_query)



    def _handle_zeroOnePoints(self, sceneImage, queryImage,**kwargs):
        result,w_h_range = self._template_match(sceneImage, queryImage,**kwargs)
        return result,w_h_range


    def _onePoints(self, pts_query, pts_scene, img_scene, img_query):
        """返回一对对匹配特征点情形下的识别结果."""
        middle_point = [int(pts_scene[0]), int(pts_scene[1])]
        pypts = []
        # 从唯一匹配点扩张出目标区域:(注意整数计算要转成浮点数结果!)
        h, w = img_query.shape[:2]
        h_s, w_s = img_scene.shape[:2]

        # 超出左边界取0, 超出右边界取w_s-1, 超出下边界取0, 超出上边界取h_s-1
        x_min, x_max = max(int(pts_scene[0] - pts_query[0]), 0), min(int(pts_scene[0] + w - pts_query[0]), w_s - 1)
        y_min, y_max = max(int(pts_scene[1] - pts_query[1]), 0), min(int(pts_scene[1] + h - pts_query[1]), h_s - 1)

        # 目标矩形的角点按左上、左下、右下、右上的点序：(x_min,y_min)(x_min,y_max)(x_max,y_max)(x_max,y_min)
        pts = np.float32([[x_min, y_min], [x_min, y_max], [x_max, y_max], [x_max, y_min]]).reshape(-1, 1, 2)
        for npt in pts.astype(int).tolist():
            pypts.append(tuple(npt[0]))

        return middle_point, pypts, [x_min, x_max, y_min, y_max, w, h]

    def _twoPoints(self, pts_query1, pts_query2, pts_scene1, pts_scene2, img_scene, img_query):
        """返回两对匹配特征点情形下的识别结果."""
        # 先算出中心点(在im_source中的坐标)：

        middle_point = [int((pts_scene1[0] + pts_scene2[0]) / 2), int((pts_scene1[1] + pts_scene2[1]) / 2)]
        pypts = []
        # 如果特征点同x轴或同y轴(无论src还是sch中),均不能计算出目标矩形区域来,此时返回值同good=1情形
        if pts_query1[0] == pts_query2[0] or pts_query1[1] == pts_query2[1] or pts_scene1[0] == pts_scene2[0] or \
                pts_scene1[1] == pts_scene2[1]:
            logger.debug('Deal twoPoints as one')
            # confidence = self.one_point_confidence
            # one_match = self.generate_result(middle_point, pypts, confidence)
            # return self._handle_onePoints()
            pts_query = [int((pts_query1[0] + pts_query2[0]) / 2), int((pts_query1[1] + pts_query2[1]) / 2)]
            pts_scene = [int((pts_scene1[0] + pts_scene2[0]) / 2), int((pts_scene1[1] + pts_scene2[1]) / 2)]
            return self._onePoints(pts_query, pts_scene, img_scene, img_query)

        # 计算x,y轴的缩放比例：x_scale、y_scale,从middle点扩张出目标区域:(注意整数计算要转成浮点数结果!)
        h, w = img_query.shape[:2]
        h_s, w_s = img_scene.shape[:2]
        x_scale = abs(1.0 * (pts_scene2[0] - pts_scene1[0]) / (pts_query2[0] - pts_query1[0]))
        y_scale = abs(1.0 * (pts_scene2[1] - pts_scene1[1]) / (pts_query2[1] - pts_query1[1]))
        if x_scale-y_scale>0.3:
            y_scale=min(max(y_scale,1),1.3)
            x_scale =y_scale

        if y_scale - x_scale > 0.3:
            x_scale=min(max(x_scale,1),1.3)
            y_scale =x_scale
        # 得到scale后需要对middle_point进行校正,并非特征点中点,而是映射矩阵的中点。
        query_middle_point = int((pts_query1[0] + pts_query2[0]) / 2), int((pts_query1[1] + pts_query2[1]) / 2)
        middle_point[0] = middle_point[0] - int((query_middle_point[0] - w / 2) * x_scale)
        middle_point[1] = middle_point[1] - int((query_middle_point[1] - h / 2) * y_scale)
        middle_point[0] = max(middle_point[0], 0)  # 超出左边界取0  (图像左上角坐标为0,0)
        middle_point[0] = min(middle_point[0], w_s - 1)  # 超出右边界取w_s-1
        middle_point[1] = max(middle_point[1], 0)  # 超出上边界取0
        middle_point[1] = min(middle_point[1], h_s - 1)  # 超出下边界取h_s-1

        # 计算出来rectangle角点的顺序：左上角->左下角->右下角->右上角, 注意：暂不考虑图片转动
        # 超出左边界取0, 超出右边界取w_s-1, 超出下边界取0, 超出上边界取h_s-1
        x_min, x_max = int(max(middle_point[0] - (w * x_scale) / 2, 0)), int(
            min(middle_point[0] + (w * x_scale) / 2, w_s - 1))
        y_min, y_max = int(max(middle_point[1] - (h * y_scale) / 2, 0)), int(
            min(middle_point[1] + (h * y_scale) / 2, h_s - 1))
        # 目标矩形的角点按左上、左下、右下、右上的点序：(x_min,y_min)(x_min,y_max)(x_max,y_max)(x_max,y_min)
        pts = np.float32([[x_min, y_min], [x_min, y_max], [x_max, y_max], [x_max, y_min]]).reshape(-1, 1, 2)
        for npt in pts.astype(int).tolist():
            pypts.append(tuple(npt[0]))

        return middle_point, pypts, [x_min, x_max, y_min, y_max, w, h]


    def _template_match(self, img_scene, img_query,**kwargs):

        h, w = img_query.shape[:2]
        result = TemplateMatcher().searchImage(img_query, img_scene, similarity=kwargs.get("similarity"), gray=kwargs.get("gray"), zoom=0, scaleMatch=True,is_transparent=0)
        result.method='feature_template'
        rect=result.__getattribute__('rect')
        if rect:
            x_min, y_min, x_max, y_max = rect
            w_h_range=[x_min, x_max, y_min, y_max,w,h]
            return result,w_h_range
        else:

            return result,None

    def _detectResult_check(self, w_h_range):
        """校验识别结果区域大小是否符合常理."""
        x_min, x_max, y_min, y_max, w, h = w_h_range
        tar_width, tar_height = x_max - x_min, y_max - y_min
        # 如果src_img中的矩形识别区域的宽和高的像素数＜5,则判定识别失效。认为提取区域待不可能小于5个像素。(截图一般不可能小于5像素)
        if tar_width < 5 or tar_height < 5:
            logger.error("In src_image, Taget area: width or height < 5 pixel.")
            return False
        # 如果矩形识别区域的宽和高,与sch_img的宽高差距超过2倍(屏幕像素差不可能有2倍),认定为识别错误。
        if tar_width < 0.4 * w or tar_width > 2 * w or tar_height < 0.4 * h or tar_height > 2 * h:
            logger.error("Target area is 2 times bigger or 0.4 times smaller than sch_img.")
            return False

        return True
    def _judge_result(self, img_query, img_detect):
        img_query_mean = []
        img_detect_mean = []

        s_h, s_w = img_detect.shape[:2]
        q_h, q_w = img_query.shape[:2]

        for i in range(1):

            scene_l = img_detect[:, 0:int(s_w / 2)]
            scene_r = img_detect[:, int(s_w / 2):s_w]
            query_l = img_query[:, 0:int(q_w / 2)]
            query_r = img_query[:, int(q_w / 2):q_w]
            img_query_mean.append(np.mean(query_l[:, :, i]))
            img_query_mean.append(np.mean(query_r[:, :, i]))
            img_detect_mean.append(np.mean(scene_l[:, :, i]))
            img_detect_mean.append(np.mean(scene_r[:, :, i]))
        judge_rgb = max(abs(np.array(img_query_mean) - np.array(img_detect_mean)))
        img_query_crop=img_query[int(q_h/4):int(q_h/4*3),int(q_w/4):int(q_w/4*3)]
        img_detect_crop=img_detect[int(s_h/2-q_h/4):int(s_h/2+q_h/4),int(s_w/2-q_w/4):int(s_w/2+q_w/4)]
        img_query_hsv = cv2.cvtColor(img_query_crop, cv2.COLOR_BGR2HSV)
        img_detect_hsv = cv2.cvtColor(img_detect_crop, cv2.COLOR_BGR2HSV)
        img_query_v=img_query_hsv[:,:,2]
        img_detect_v =img_detect_hsv[:,:,2]
        judge_v=abs(np.mean(img_query_v) - np.mean(img_detect_v))

        return judge_rgb,judge_v

    def _judge_result_template(self, img_query, img_detect):
        img_query_mean = []
        img_detect_mean = []

        s_h, s_w = img_detect.shape[:2]
        q_h, q_w = img_query.shape[:2]

        for i in range(1):

            img_query_mean.append(np.mean(img_query[:, :, i]))
            img_detect_mean.append(np.mean(img_detect[:, :, i]))
        judge_rgb = max(abs(np.array(img_query_mean) - np.array(img_detect_mean)))
        img_query_crop=img_query[int(q_h/4):int(q_h/4*3),int(q_w/4):int(q_w/4*3)]
        img_query_hsv = cv2.cvtColor(img_query, cv2.COLOR_BGR2HSV)
        img_detect_hsv = cv2.cvtColor(img_detect, cv2.COLOR_BGR2HSV)
        img_query_v=img_query_hsv[:,:,2]
        img_detect_v =img_detect_hsv[:,:,2]
        judge_v=abs(np.mean(img_query_v) - np.mean(img_detect_v))

        return judge_rgb,judge_v

    def _judge_points(self,kp_query,kp_scene, good):
        pts_query_x = []
        for kp in kp_query:
            pts_query_x.append(kp.pt[0])
        pts_query_distribute = int(np.max(pts_query_x)) -int(np.min(pts_query_x))

        num = len(good)
        pts_scene_x = []
        for p in range(num):
            pts_scene_x.append(kp_scene[good[p].trainIdx].pt[0])

        pts_scene_xmin = int(np.min(pts_scene_x))
        pts_scene_xmax = int(np.max(pts_scene_x))
        pts_scene_distribute=pts_scene_xmax-pts_scene_xmin

        # pts_scene_middle = 0
        if pts_scene_distribute < (pts_query_distribute/4):
            logger.debug('points distribute is err,pts_scene_distribute is smaller than 1/4 of pts_query_distribute!' )
            logger.debug('pts_scene_distribute:%s'%pts_scene_distribute)
            logger.debug('pts_query_distribute:%s' % pts_query_distribute)
            return False
        if pts_scene_distribute > 80:
            for s_p in pts_scene_x:
                if s_p > pts_scene_xmin + pts_scene_distribute*1/3 and s_p<pts_scene_xmax-pts_scene_distribute*1/3:
                    # pts_scene_middle += 1
                    return True
            logger.debug('pts_scene_middle is None,not match!')
            return False

        return True


    def cal_ccoeff_confidence(self, img_scene, img_query):
        """求取两张图片的可信度,使用TM_CCOEFF_NORMED方法."""

        img_scene = cv2.cvtColor(img_scene, cv2.COLOR_BGR2GRAY)
        img_query = cv2.cvtColor(img_query, cv2.COLOR_BGR2GRAY)
        res = cv2.matchTemplate(img_scene, img_query, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        confidence = max_val
        return confidence

    def cal_rgb_confidence(self, img_query_rgb, img_scene_rgb,matched_points):
        """同大小彩图计算相似度."""
        # img_scene_HLS=cv2.cvtColor(img_scene_rgb, cv2.COLOR_BGR2HLS)[2]
        # img_query_HLS=cv2.cvtColor(img_query_rgb,cv2.COLOR_BGR2HLS)[2]
        # binary_threshold = np.mean(img_query_L)
        # # print(binary_threshold)
        # img_scene_gray = cv2.cvtColor(img_scene_rgb, cv2.COLOR_BGR2GRAY)
        # img_query_gray = cv2.cvtColor(img_query_rgb, cv2.COLOR_BGR2GRAY)
        #
        # img_scene_L = cv2.adaptiveThreshold(img_scene_L, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 5, 10)
        # img_query_L = cv2.adaptiveThreshold(img_query_L, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 5, 10)
        # cv2helper.show(img_query_rgb)
        # cv2helper.show(img_scene_rgb)
        # # res_temp_l = cv2.matchTemplate(img_scene, img_query, cv2.TM_CCOEFF_NORMED)
        # # min_val_l, max_val_l, min_loc_l, max_loc_l = cv2.minMaxLoc(res_temp_l)
        # retval, img_scene_L = cv2.threshold(img_scene_L, binary_threshold, 255, cv2.THRESH_BINARY)
        # retval, img_query_L = cv2.threshold(img_query_L, binary_threshold, 255, cv2.THRESH_BINARY)
        s_h, s_w = img_scene_rgb.shape[:2]
        q_h, q_w = img_query_rgb.shape[:2]

        scene_l = img_scene_rgb[:, 0:int(s_w / 3)]
        scene_m = img_scene_rgb[:, int(s_w / 3):int(s_w / 3 * 2)]
        scene_r = img_scene_rgb[:, int(s_w / 3 * 2):s_w]

        query_l = img_query_rgb[:, 0:int(q_w / 3)]
        query_m = img_query_rgb[:, int(q_w / 3):int(q_w / 3 * 2)]
        query_r = img_query_rgb[:, int(q_w / 3 * 2):q_w]

        # scene_l = img_scene_rgb[:, 0:int(s_w / 4)]
        # scene_m1 = img_scene_rgb[:, int(s_w / 4):int(s_w / 2)]
        # scene_m2 = img_scene_rgb[:, int(s_w /2 ):int(s_w /4*3)]
        # scene_r = img_scene_rgb[:, int(s_w / 4*3):s_w]
        #
        # query_l = img_query_rgb[:, 0:int(q_w / 4)]
        # query_m1 = img_query_rgb[:, int(q_w / 4):int(q_w /  2)]
        # query_m2 = img_query_rgb[:, int(q_w / 2):int(q_w / 4*3)]
        #
        # query_r = img_query_rgb[:, int(q_w / 4 * 3):q_w]

        # scene_l = img_scene_rgb[:, 0:int(s_w / 2)]
        # scene_r = img_scene_rgb[:, int(s_w / 2):s_w]
        #
        # query_l = img_query_rgb[:, 0:int(q_w / 2)]
        # query_r = img_query_rgb[:, int(q_w /2):q_w]

        res_temp_l = cv2.matchTemplate(scene_l, query_l, cv2.TM_CCOEFF_NORMED)
        min_val_l, max_val_l, min_loc_l, max_loc_l = cv2.minMaxLoc(res_temp_l)
        res_temp_m = cv2.matchTemplate(scene_m, query_m, cv2.TM_CCOEFF_NORMED)
        min_val_m, max_val_m, min_loc_m, max_loc_m = cv2.minMaxLoc(res_temp_m)
        # res_temp_m2 = cv2.matchTemplate(scene_m2, query_m2, cv2.TM_CCOEFF_NORMED)
        # min_val_m2, max_val_m2, min_loc_m2, max_loc_m2 = cv2.minMaxLoc(res_temp_m2)
        res_temp_r = cv2.matchTemplate(scene_r, query_r, cv2.TM_CCOEFF_NORMED)
        min_val_r, max_val_r, min_loc_r, max_loc_r = cv2.minMaxLoc(res_temp_r)
        confidence_min = min(max_val_l, max_val_m, max_val_r)
        confidence_max = max(max_val_l, max_val_m, max_val_r)
        # if matched_points>15:
        #     if confidence_max-confidence_min < 0.2:
        #         confidence=confidence_min
        #     else:
        #         confidence=0
        # else:
        #     if confidence_max-confidence_min < 0.3:
        #         confidence=confidence_min
        #     else:
        #         confidence=0
        confidence=confidence_min
        return confidence

    def _matchFeature(self, sceneImage, queryImage, threshold, rgb=True, good_ratio=filter_ratio, **kwargs):
        feature_result=MatchResult()
        feature_result.method='feature'

        sceneImg = sceneImage.copy()
        queryImg = queryImage.copy()
        queryImageHeight, queryImageWidth = queryImage.shape[:2]
        sceneImageHeight, sceneImageWidth = sceneImage.shape[:2]
        # queryImgH = queryImageHeight
        # queryImgW = queryImageWidth
        # sceneImgH = sceneImageHeight
        # sceneImgW = sceneImageWidth
        method = kwargs.get('method', 'sift-flann')
        position_lock=kwargs.get('position_lock')
        animation=kwargs.get('animation')
        is_word = kwargs.get('is_word')
        is_transparent = kwargs.get('is_transparent')
        is_highlight=kwargs.get('is_highlight')
        # if position_lock==1:
        position = kwargs.get('position')
        logger.debug('templateImg position:%s' % str(position))

        adjustThreshold=kwargs.get('adjustThreshold')
        if position and len(position) == 4:
            logger.info('TemplateImg position is locked,crop Img!')
            crop_position=_getPosition(queryImage,sceneImage, position)
            crop_x_min, crop_y_min, crop_x_max, crop_y_max=crop_position
            sceneImage=sceneImage[crop_y_min:crop_y_max, crop_x_min:crop_x_max]
        else:
            logger.info('TemplateImg position is unlocked')
            crop_x_min, crop_y_min, crop_x_max, crop_y_max = 0, 0, 0, 0

        if position and len(position) == 4:
            res_simpleColor = judge_SimpleColor(queryImage)
            if res_simpleColor:
                logger.info('___res_simpleColor____')
                sim, rect = transparent(queryImage, sceneImage)
                if sim >= 0.6:
                    return feature_result, (rect[0] + crop_x_min, rect[1] + crop_y_min, rect[0] + rect[2] + crop_x_min,
                                        rect[1] + rect[3] + crop_y_min)

        if is_highlight==1 and position and len(position) == 4:
            judge_highlight = highlight(sceneImage, sceneImg)
            if judge_highlight is False:
                judge_highlight2 = highlight(sceneImage, queryImg)
                if judge_highlight2 is False:
                    return feature_result, None

        if is_transparent==1 or is_highlight==1:
            sim,rect=transparent(queryImage,sceneImage)
            logger.debug('****transparent or is_highlight:%s'%sim)
            if position and len(position) == 4:
                if sim>=0.6:
                    return feature_result,(rect[0]+crop_x_min, rect[1]+crop_y_min, rect[0] + rect[2]+crop_x_min, rect[1] + rect[3]+crop_y_min)
            else:
                if sim>=0.8:
                    return feature_result,(rect[0] + crop_x_min, rect[1] + crop_y_min, rect[0] + rect[2] + crop_x_min,rect[1] + rect[3] + crop_y_min)
        # cv2helper.show(sceneImage)
        detector, matcher = self._init(method)
        queryFeaturePoints, queryDesc = self._getKeyPoints(detector,queryImage, method='sift-flann')
        sceneFeaturePoints, sceneDesc = self._getKeyPoints(detector,sceneImage, method='sift-flann')
        good_kp_pairs=[]
        if len(sceneFeaturePoints)>1 and len(queryFeaturePoints)>1:

            filtered_query_kp, filtered_scene_kp, good_kp_pairs = self._filterMatchedPoints(sceneFeaturePoints, sceneDesc,
                                                                                            queryFeaturePoints, queryDesc,
                                                                                            matcher, good_ratio,
                                                                                   queryImageWidth)

        else:
            logger.debug('No sceneFeaturePoints!No queryFeaturePoints!')
            good_kp_pairs==None
        logger.info('Feature match! ')
        resizeTag = False
        resizeM = 1
        templateMatchTag = False
        if is_word == 1 and len(good_kp_pairs)>1 and len(queryFeaturePoints) > 20:
            logger.info('Template image is word,feature points is enough ,need judge_points!')
            pts_scene_middle = self._judge_points(filtered_query_kp, filtered_scene_kp, good_kp_pairs)
            # if  pts_scene_middle==0:
            if not pts_scene_middle:
                logger.debug('pts_scene_middle is None!')
                return feature_result,None

        feature_result.miscellaneous['good_kp_pairs']=len(good_kp_pairs)
        feature_result.miscellaneous['queryFeaturePoints'] = len(queryFeaturePoints)
        logger.debug('queryFeaturePoints is:%s' % len(queryFeaturePoints))
        if good_kp_pairs==None or len(good_kp_pairs) == 0 or len(good_kp_pairs) == 1:
            logger.debug('good_kp_pairs is:%s' % len(good_kp_pairs))
            queryFeaturePoints_T=25
            # if animation==1:
            #     queryFeaturePoints_T=15
            if len(queryFeaturePoints) <= queryFeaturePoints_T:

                templateMatchTag=True
                logger.debug('Not enough feature points,template match!')
                template_result,w_h_range = self._handle_zeroOnePoints(sceneImage, queryImage,**kwargs)
                if w_h_range:

                    templateRect = template_result.rect
                    templateRect=[templateRect[0]+crop_x_min,templateRect[1]+crop_y_min,templateRect[2]+crop_x_min,templateRect[3]+crop_y_min]
                    template_result.rect=templateRect
                    logger.debug('0 points:template_result:%s'%template_result)
                    logger.debug('w_h_range:%s'% w_h_range)
                else:
                    template_result.rect=None
                    logger.debug('Template is also not matched!')
                    return template_result,None
            else:
                logger.debug('Enough feature points, not enough good points, feature is not matched!')
                return feature_result,None


        elif len(good_kp_pairs) == 2:

            logger.debug('good_kp_pairs is:%s' % len(good_kp_pairs))
            # 匹配点对为2,根据点对求出目标区域,据此算出可信度：
            origin_result = self._handle_twoPoints(sceneImage, queryImage, filtered_scene_kp, filtered_query_kp,
                                                   good_kp_pairs)
            if isinstance(origin_result, dict):
                if self.one_point_confidence >= threshold:
                    return feature_result,origin_result
                else:
                    return feature_result,None
            else:
                middle_point, pypts, w_h_range = self._handle_twoPoints(sceneImage, queryImage, filtered_scene_kp,
                                                                        filtered_query_kp, good_kp_pairs)
        elif len(good_kp_pairs) == 3:

            logger.debug('good_kp_pairs is:%s' % len(good_kp_pairs))
            # 匹配点对为3,取出点对,求出目标区域,据此算出可信度：
            origin_result = self._handle_threePoints(sceneImage, queryImage, filtered_scene_kp, filtered_query_kp,
                                                     good_kp_pairs)
            if isinstance(origin_result, dict):
                if self.one_point_confidence >= threshold:
                    return feature_result,origin_result
                else:
                    return feature_result,None
            else:
                middle_point, pypts, w_h_range = self._handle_threePoints(sceneImage, queryImage, filtered_scene_kp,
                                                                          filtered_query_kp, good_kp_pairs)
        else:

            logger.debug('good_kp_pairs is:%s' % len(good_kp_pairs))

            # 匹配点对 >= 4个,使用单矩阵映射求出目标区域,据此算出可信度：
            middle_point, pypts, w_h_range = self._handle_manyPoints(sceneImage, queryImage, filtered_scene_kp,
                                                                     filtered_query_kp, good_kp_pairs)
            # print(w_h_range)

        # 第四步：根据识别区域,求出结果可信度,并将结果进行返回:
        # 对识别结果进行合理性校验: 小于5个像素的,或者缩放超过5倍的,一律视为不合法直接raise.
        result_check = self._detectResult_check(w_h_range)


        if result_check:
            x_min, x_max, y_min, y_max, w, h = w_h_range
            logger.debug('simple result_check is correct!')
        else:
            logger.debug('simple result_check is error!')
            return feature_result,None

        detect_img = sceneImage[y_min:y_max, x_min:x_max]
        if is_highlight == 1:
            judge_highlight = highlight(detect_img, sceneImg)
            if judge_highlight is False:
                judge_highlight2 = highlight(sceneImage, queryImg)
                if judge_highlight2 is False:
                    return feature_result, None

        if len(good_kp_pairs)>20:
            judge_rgb, judge_v = self._judge_result(queryImage, detect_img)
            if judge_v>40 and judge_rgb>40:
                return feature_result, None
            x_min = x_min + crop_x_min
            y_min = y_min + crop_y_min
            x_max = x_max + crop_x_min
            y_max = y_max + crop_y_min
            logger.debug('good points is enough ,no need do judge_result !good_kp_pairs :%s'% len(good_kp_pairs))
            if 'showResult' in kwargs and kwargs['showResult']:
                self._showResult(queryImg, sceneImg, (x_min, y_min, x_max, y_max))
                # self._show_feature_match_result(queryImg, sceneImg, sceneFeaturePoints, queryFeaturePoints,
                # good_kp_pairs,
                # resizeTag, resizeM, (x_min, y_min, x_max, y_max))
            return feature_result,(x_min, y_min, x_max, y_max)



        if is_transparent == 1 or animation == 1 or is_highlight==1:

            x_min = x_min + crop_x_min
            y_min = y_min + crop_y_min
            x_max = x_max + crop_x_min
            y_max = y_max + crop_y_min
            if templateMatchTag:
                if 'showResult' in kwargs and kwargs['showResult']:
                    self._showResult(queryImg, sceneImg, (x_min, y_min, x_max, y_max))
                return template_result, (x_min, y_min, x_max, y_max)
            else:
                if 'showResult' in kwargs and kwargs['showResult']:
                    self._showResult(queryImg, sceneImg, (x_min, y_min, x_max, y_max))

                return feature_result, (x_min, y_min, x_max, y_max)

        else:
            if templateMatchTag:

                judge_rgb, judge_v = self._judge_result_template(queryImage, detect_img)
                logger.debug('start judge_result_template!')
                logger.debug('judge_rgb:%s' % judge_rgb)
                logger.debug('judge_v:%s' % judge_v)

                judge_T=15
                if adjustThreshold==1:
                    logger.debug('Use adjustThreshold!')
                    judge_T=20

                if judge_rgb < judge_T and judge_v < judge_T:
                    x_min = x_min + crop_x_min
                    y_min = y_min + crop_y_min
                    x_max = x_max + crop_x_min
                    y_max = y_max + crop_y_min
                    if 'showResult' in kwargs and kwargs['showResult']:
                        self._showResult(queryImg, sceneImg, (x_min, y_min, x_max, y_max))
                        # self._show_feature_match_result(queryImg, sceneImg, sceneFeaturePoints, queryFeaturePoints,
                        #                                             good_kp_pairs,
                        #                                             resizeTag, resizeM, (x_min, y_min, x_max, y_max))
                    logger.debug('return template_result:%s'%template_result)
                    logger.debug('x_min:%s' % x_min)
                    return template_result,(x_min, y_min, x_max, y_max)
                else:
                    template_result.rect=None
                    return template_result,None
            else:
                judge_rgb, judge_v = self._judge_result(queryImage, detect_img)
                logger.debug('start judge_result:')
                logger.debug('judge_rgb:%s'% judge_rgb)
                logger.debug('judge_v:%s' % judge_v)

                if judge_rgb > 100 or judge_v > 100:
                    return feature_result,None
                judge_T_min = 10
                judge_T_max = 35
                if adjustThreshold == 1:
                    logger.debug('Use adjustThreshold!')
                    judge_T_min = 15
                    judge_T_max = 40

                if (judge_rgb<judge_T_max and judge_v<judge_T_max )or judge_rgb<judge_T_min:
                    x_min = x_min + crop_x_min
                    y_min = y_min + crop_y_min
                    x_max = x_max + crop_x_min
                    y_max = y_max + crop_y_min
                    logger.debug('judge_result is correct, image is matched!')
                    if 'showResult' in kwargs and kwargs['showResult']:
                        self._showResult(queryImg, sceneImg, (x_min, y_min, x_max , y_max ))
                        # self._show_feature_match_result(queryImg, sceneImg, sceneFeaturePoints, queryFeaturePoints,
                        #                                             good_kp_pairs,
                        #                                             resizeTag, resizeM, (x_min, y_min, x_max, y_max))
                    logger.debug('return feature_result:%s' % feature_result)
                    logger.debug('x_min:%s' % x_min)
                    return feature_result,(x_min, y_min, x_max , y_max )
                else:
                    logger.debug('judge_result is error, image is not matched!')
                    return feature_result,None



    def _show_feature_match_result(self, queryImg, sceneImg, sceneFeaturePoints, queryFeaturePoints, kp_pairs,
                                   resizeTag, resizeM, rlt):

        if rlt:
            h2, w2 = sceneImg.shape[:2]
            h1, w1 = queryImg.shape[:2]
            if len(sceneImg.shape) > 2:
                vis = cv2helper.eval2('np.zeros')((max(h1, h2), w1 + w2, 3), cv2helper.eval2('np.uint8'))
            else:
                vis = cv2helper.eval2('np.zeros')((max(h1, h2), w1 + w2), cv2helper.eval2('np.uint8'))
            # print('rlt',rlt)
            vis[:h1, :w1] = queryImg
            vis[:h2, w1:w1 + w2] = sceneImg
            x1 = int(rlt[0] / resizeM)
            y1 = int(rlt[1] / resizeM)
            x2 = int(rlt[2] / resizeM)
            y2 = int(rlt[3] / resizeM)
            cv2helper.eval2('cv2.rectangle')(vis, (x1 + w1, y1), (x2 + w1, y2), (0, 0, 255), 2)

        p1 = cv2helper.eval2('np.int32')([queryFeaturePoints[kpp.queryIdx].pt for kpp in kp_pairs])

        if resizeTag:
            w1 = resizeM * w1
        p2 = cv2helper.eval2('np.int32')([sceneFeaturePoints[kpp.trainIdx].pt for kpp in kp_pairs]) + (w1, 0)
        green = (0, 255, 0)

        for (x1, y1), (x2, y2) in zip(p1, p2):
            if resizeTag:
                x1 = int(x1 / resizeM)
                y1 = int(y1 / resizeM)
                x2 = int(x2 / resizeM)
                y2 = int(y2 / resizeM)
            col = green
            cv2helper.eval2('cv2.circle')(vis, (x1, y1), 2, col, -1)
            cv2helper.eval2('cv2.circle')(vis, (x2, y2), 2, col, -1)

        for (x1, y1), (x2, y2) in zip(p1, p2):
            if resizeTag:
                x1 = int(x1 / resizeM)
                y1 = int(y1 / resizeM)
                x2 = int(x2 / resizeM)
                y2 = int(y2 / resizeM)
            cv2helper.eval2('cv2.line')(vis, (x1, y1), (x2, y2), green)

        cv2helper.show(vis)

    def _showResult(self, queryData, sceneData, rlt):
        templ_h, templ_w = queryData.shape[:2]
        # for pt in pts:
        #     cv2helper.eval2('cv2.rectangle')(sceneData, pt, (pt[0]+templ_w, pt[1]+templ_h), (0,0,255), 2)

        h1, w1 = queryData.shape[:2]
        h2, w2 = sceneData.shape[:2]

        if len(sceneData.shape) > 2:
            vis = cv2helper.eval2('np.zeros')((max(h1, h2), w1 + w2, 3))
        else:
            vis = cv2helper.eval2('np.zeros')((max(h1, h2), w1 + w2))

        vis[:h1, :w1] = queryData
        vis[:h2, w1:w1 + w2] = sceneData

        x1 = rlt[0]
        y1 = rlt[1]
        x2 = rlt[2]
        y2 = rlt[3]
        cv2helper.eval2('cv2.rectangle')(vis, (x1 + w1, y1), (x2 + w1, y2), (0, 0, 255), 2)
        # x1,y1,x2,y2 =self._rect(h1,w1,h2,w2,corners,resizeTag,resizeM)

        cv2.imwrite('vis.jpg', vis)
        tmp = cv2.imread('vis.jpg')
        cv2helper.show(tmp)
        os.remove('vis.jpg')

    def searchImage(self, queryImg, sceneImg, similarity=0.65, gray=False,adjustThreshold=0, **kwargs):
        result=MatchResult()
        result.method = 'feature'
        start = time.time()


        scaleRatio = None
        queryImageData = None
        if isinstance(queryImg, str):
            queryImageData = self._getImageData(queryImg, gray)
        elif cv2helper.isNdarray(queryImg):
            queryImageData = queryImg
        else:
            raise TypeError('unknown type:%s' % type(queryImg))

        trainImageData = None
        if isinstance(sceneImg, str):
            trainImageData = self._getImageData(sceneImg, gray)
        elif cv2helper.isNdarray(sceneImg):
            trainImageData = sceneImg
        else:
            raise TypeError('unknown type:%s' % type(sceneImg))

        if trainImageData is None or queryImageData is None:
            logger.error('No trainImageData or queryImageData')
            end = time.time()
            time_cost = end - start
            result.time = time_cost
            result.parameters = kwargs
            return result


        kwargs.update(similarity=similarity)
        kwargs.update(gray=gray)
        kwargs.update(adjustThreshold=adjustThreshold)
        threshold=0.65
        if adjustThreshold==1:
            self.filter_ratio = 0.65
            threshold = 0.6
        match_result,rlt = self._matchFeature(trainImageData, queryImageData, threshold=threshold, rgb=True,
                                 good_ratio=self.filter_ratio, **kwargs)

        ##固定位置匹配不到————如果检测到黑边，去掉固定位置再次检测
        if rlt is None :

            position = kwargs.get('position')
            if position and len(position) == 4:
                have_specialBorder=specialBorder(trainImageData)
                if have_specialBorder:
                    kwargs['position']=None
                    match_result, rlt = self._matchFeature(trainImageData, queryImageData, threshold=threshold,
                                                           rgb=True,
                                                           good_ratio=self.filter_ratio, **kwargs)
        end = time.time()
        time_cost = end - start
        result.time = time_cost
        if match_result.__getattribute__('method')!='feature':
            logger.debug('____________match_result:%s' % match_result)
            return match_result

        result.rect =rlt
        result.parameters = kwargs
        result.miscellaneous['filter_ratio'] = self.filter_ratio
        result.miscellaneous['threshold'] = threshold
        if 'good_kp_pairs' in match_result.miscellaneous:
            result.miscellaneous['good_kp_pairs']=match_result.miscellaneous['good_kp_pairs']
            result.miscellaneous['queryFeaturePoints'] = match_result.miscellaneous['queryFeaturePoints']
            logger.debug('___________result:%s' % result)
        return  result

