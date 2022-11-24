# -*- coding:UTF-8 -*-
"""
基于opencv的图片比较。依赖于logger模块和cv2helper模块。
"""
import os
import cv2
import time
import logging
import numpy as np
from .utils import MatchResult,_getPosition,transparent,judge_SimpleColor
from . import cv2helper

_DEBUG_HANDLERS = {}
logger = logging.getLogger('cvmatcher')
logger.setLevel(logging.DEBUG)
_filter = logging.Filter(name='cvmatcher')


def addHandler(hdlr):
    global _DEBUG_HANDLERS, logger
    clsName = hdlr.__class__.__name__
    if clsName not in _DEBUG_HANDLERS:
        hdlr.addFilter(_filter)
        logger.addHandler(hdlr)
        _DEBUG_HANDLERS[clsName] = hdlr


def pHash(img):
    """get image pHash value"""

    #调整为灰色
    if len(img.shape) > 2:
        img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    h, w = img.shape[:2]
    if h > 32 and w > 32:
        #调整图片为32x32灰度图片
        img=cv2.resize(img,(32,32),interpolation=cv2.INTER_CUBIC)

        #创建二维列表
        h, w = img.shape[:2]
        vis0 = np.zeros((h,w), np.float32)
    elif h > 16 and w > 16:
        #调整图片为32x32灰度图片
        img=cv2.resize(img,(16,16),interpolation=cv2.INTER_CUBIC)

        #创建二维列表
        h, w = img.shape[:2]
        vis0 = np.zeros((h,w), np.float32)
    else:
        #调整图片为32x32灰度图片
        img=cv2.resize(img,(8,8),interpolation=cv2.INTER_CUBIC)

        #创建二维列表
        h, w = img.shape[:2]
        vis0 = np.zeros((h,w), np.float32)

#     #调整图片为32x32灰度图片
#     img=cv2.resize(img,(32,32),interpolation=cv2.INTER_CUBIC)
#
#     #创建二维列表
#     h, w = img.shape[:2]
#     vis0 = np.zeros((h,w), np.float32)
    vis0[:h,:w] = img       #填充数据

    #二维Dct变换
    vis1 = cv2.dct(cv2.dct(vis0))
    #cv.SaveImage('a.jpg',cv.fromarray(vis0)) #保存图片
    vis1.resize(8,8)

    #把二维list变成一维list
    img_list = vis1.flatten()#flatten(vis1.tolist())

    #计算均值
    avg = sum(img_list)*1./len(img_list)
    avg_list = ['0' if i<avg else '1' for i in img_list]

    #得到哈希值
    return ''.join(['%x' % int(''.join(avg_list[x:x+4]),2) for x in range(0,64,4)])

def hamming(h1, h2):
    '''汉明距离'''
    cnt = len(h1)
    total = 0
    for i in range(cnt):
        c1 = int(h1[i],16)
        c2 = int(h2[i],16)
        h, d = 0, c1 ^ c2

        while d:
            h += 1
            d &= d - 1
        #print h
        total += h
    return total

def compareByHamming(img1, img2, similarity=5):
    if not os.path.exists(img1):
        logger.error('%s not found' % img1)
        return False
    if not os.path.exists(img2):
        logger.error('%s not found' % img2)
        return False
    imgData1 = cv2.imread(img1)
    imgData2 = cv2.imread(img2)
    h1 = pHash(imgData1)
    h2 = pHash(imgData2)
    dis = hamming(h1, h2)
    if dis <= similarity:
        return True
    return False

class Hist(object):
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

    def _getHist(self, grayImg, colorBin=8):
        hist = cv2.calcHist([grayImg], [0], None, [colorBin], [0, 255])
        return cv2.normalize(hist, None).flatten()  # opencv 3.x

    def compare(self, img1, img2, gray=1, method='CHISQR', **kwargs):
        if gray != 1:
            raise NotImplementedError('gray must be 1')

        if method != 'CHISQR':
            raise NotImplementedError('method must be CHISQR')

        img1Data = None
        if isinstance(img1, str):
            img1Data = self._getImageData(img1, gray)

        elif cv2helper.isNdarray(img1):
            if gray and len(img1.shape) == 3:
                img1Data = cv2helper.cvtColor(img1)
            else:
                img1Data = img1
        else:
            raise TypeError('unknown type:%s' % type(img1))

        img2Data = None
        if isinstance(img2, str):
            img2Data = self._getImageData(img2, gray)
        elif cv2helper.isNdarray(img2):
            if gray and len(img2.shape) == 3:
                img2Data = cv2helper.cvtColor(img2)
            else:
                img2Data = img2
        else:
            raise TypeError('unknown type:%s' % type(img2))

        if img1Data is None or img2Data is None:
            raise ValueError('empty data')

        colorBin = 8
        if 'colorBin' in kwargs:
            colorBin = kwargs['colorBin']
        hist1 = self._getHist(img1Data, colorBin=colorBin)
        hist2 = self._getHist(img2Data, colorBin=colorBin)

        # method - cv2.HISTCMP_CHISQR, cv2.HISTCMP_BHATTACHARYYA, cv2.HISTCMP_CORREL, cv2.HISTCMP_INTERSECT
        rlt = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CHISQR)  # [0, max), 0为最匹配， 取个经验值，小于0.1为相似
        #         print(cv2.compareHist(hist1, hist2, cv2.HISTCMP_BHATTACHARYYA))
        #         print(cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL))
        #         print(cv2.compareHist(hist1, hist2, cv2.HISTCMP_INTERSECT))
        logger.info('hist result %s'%str(rlt))
        return rlt

    def similar(self, img1, img2, similarity=0.1, gray=1, method='CHISQR', **kwargs):
        rlt = self.compare(img1, img2, gray, method)
        return (rlt <= similarity)


class TemplateMatcher(object):
    _SCALE_RATIO_CACHE = {}
    _DEBUG_HANDLERS = {}

    def __init__(self):

        self._hist = Hist()

    #         if debug:
    #             selfpid = os.getpid()
    #             logDir = getEnv('WORKSPACE', os.getcwd())
    #             filePath=os.path.join(logDir, 'cvmatcher_{name}.log'.format(name=selfpid))
    #
    #             mode = 'w'
    #             if os.path.exists(filePath):
    #                 mode = 'a'
    #
    #             if selfpid not in TemplateMatcher._DEBUG_HANDLERS: # 避免重复
    #                 if int(getEnv('CVMATCHER_STDOUT', '0')):
    #                     _stdout = handler.DebugStreamHandler()
    #                     _stdout.addFilter(_filter)
    #                     logger.addHandler(_stdout)
    #
    #                 _hdlr = handler.DebugFileHandler(filePath, mode)
    #                 _hdlr.addFilter(_filter)
    #                 logger.addHandler(_hdlr)
    #                 TemplateMatcher._DEBUG_HANDLERS[selfpid] = _hdlr

    def _reset(self, trustSimilarity, **kwargs):
        self._maxHistSimilarity = 0
        self._minHistSimilarity = 1000
        self._maxSimilarity = 0
        self._minSimilarity = 1000
        self._matchCount = 0
        self._similarity = 0
        self._histSimilarity = 0

        self._trustSimilarity = trustSimilarity
        self._badTryCount = kwargs.get('badTryCount', 2)
        self._zoom = kwargs.get('zoom', 0)
        self._zoomOutDelta = kwargs.get('zoomOutDelta', 0.2)
        self._zoomInDelta = kwargs.get('zoomInDelta', 0.2)
        self._experienceSimilarity = kwargs.get('experienceSimilarity', 0.65)
        if self._experienceSimilarity >= trustSimilarity - 0.05:
            self._experienceSimilarity = trustSimilarity - 0.05
        self._lessGoodSimilarity2 = kwargs.get('lessGoodSimilarity2', 0.6)
        if self._lessGoodSimilarity2 >= trustSimilarity - 0.1:
            self._lessGoodSimilarity2 = trustSimilarity - 0.1
        self._untrustSimilarity = kwargs.get('untrustSimilarity', 0.3)
        self._histTrustSimilarity = kwargs.get('histTrustSimilarity', 0.1)
        self._histUntrustSimilarity = kwargs.get('histUntrustSimilarity', 10)
        self._use_histSimilarity = True

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

    def _getMultiResult(self, target, loc, distance=5):
        """获取多个相似对象"""
        if loc[0].size < 2:
            return [target]
        st = time.time()
        pts = zip(*loc[::-1])
        tmp = [target]
        for pt in pts:
            if abs(pt[0] - target[0]) > distance or abs(pt[1] - target[1]) > distance:
                tmp.append(pt)

        rlt = []
        for x in range(2):
            tmp.sort(key=lambda pt: pt[x])  # 坐标点(x,y)，先x排序，后y排序
            rlt = tmp[:]
            i = 0
            while i < len(tmp) - 1:
                pt_i = tmp[i]
                j = i + 1
                while j < len(tmp):
                    pt_j = tmp[j]
                    if abs(pt_j[0] - pt_i[0]) < distance and abs(pt_j[1] - pt_i[1]) < distance:
                        if pt_j in rlt:
                            if pt_j == target and pt_i in rlt:
                                rlt.remove(pt_i)
                            else:
                                rlt.remove(pt_j)
                    else:
                        break
                    j = j + 1
                i = j
            tmp = rlt

        et = time.time()
        logger.info('time cost:%s' % str(et - st))

        return rlt

    def _matchTemplateWithSeperateChannels(self, tplData, scnData, rect):
        if len(tplData.shape) < 3:
            # 已经是单通道，不再需要分通道
            return True

        tplImgHeight, tplImgWidth = tplData.shape[:2]
        newTplImg = tplData.copy()

        distance = min(tplImgHeight, tplImgWidth)
        t = cv2.split(newTplImg)
        s = cv2.split(scnData)
        max_similarity = 0
        max_rc = None
        c = 0
        for i in range(3):
            rlt = cv2helper.matchTemplate(s[i], t[i])
            _, max_val, _, max_loc = cv2helper.minMaxLoc(rlt)
            if max_val > max_similarity:
                max_similarity = max_val
                max_rc = max_loc
                c = i
        logger.debug('rc:%s' % str(rect))
        logger.debug('channel:%s' % c)
        logger.debug('channel_rc:%s' % str(max_rc))

        if abs(max_rc[0] - rect[0]) < distance and abs(max_rc[1] - rect[1]) < distance:
            return True
        return False

    def _validate(self, img1, img2, pt, print_log=False):
        img1 = img1.copy()
        h, w = img1.shape[:2]
        img2 = cv2helper.roi(img2.copy(), (pt[0], pt[1], pt[0] + w, pt[1] + h))

        # 直方图256 bins验证， 在遇到23_t_1时判断失败
        histValue = Hist().compare(img1, img2, colorBin=256)  # 10 for 256, 0.1 for 8 (color bin)
        if print_log:
            #             print('==============>hist:  %s' % (histValue))
            logger.debug('----------pt:%s--' % str(pt))
            logger.debug('----------hist check--:%s--' % histValue)

        if histValue > 50:
            return 2
        elif histValue <= 10:
            return 0
        else:
            return 1

        # phash验证

    #         p1 = pHash(img1)
    #         p2 = pHash(img2)
    #         pHM = hamming(p1, p2)
    #         if print_log:
    # #             print('============>hamming distance:  %s' % (pHM))
    #             logger.debug('---------->pt:%s--phash and hamming distance check--:%s<---------' % (str(pt), pHM))
    #
    #         if pHM > 15:
    #             return 2
    #
    #         if histValue <= 10 and pHM <= 15:
    #             return 0
    #
    #         return 1
    #         if rlt < 10:
    #             return 0
    #         elif rlt >= 10 and rlt < 50:
    #             return 1
    #         else:
    #             return 2

    def _matchTemplate(self, tplImg, scnImg, scale=1.0, similarity=0.7, index=-1):
        tplImgHeight, tplImgWidth = tplImg.shape[:2]
        scnImgHeight, scnImgWidth = scnImg.shape[:2]
        newTplImg = tplImg.copy()
        if scale != 1.0:
            tplImgHeight = int(tplImgHeight * scale)
            tplImgWidth = int(tplImgWidth * scale)
            newTplImg = cv2helper.resize(tplImg, tplImgWidth, tplImgHeight)

        if tplImgHeight > scnImgHeight or tplImgWidth > scnImgWidth:
            return (0, None)

        self._matchCount = self._matchCount + 1
        rlt = cv2helper.matchTemplate(scnImg.copy(), newTplImg.copy())
        _, max_val, _, max_loc = cv2helper.minMaxLoc(rlt)
        logger.debug('scale:%s' % scale)
        logger.debug('height:%s' % tplImgHeight)
        logger.debug('width:%s' % tplImgWidth)
        logger.debug('searched similarity:%s' % max_val)
        logger.debug('searched point:%s' % str(max_loc))

        self._similarity = max_val
        if max_val > self._maxSimilarity:
            self._maxSimilarity = max_val
        if max_val < self._minSimilarity:
            self._minSimilarity = max_val

        if max_val > similarity:
            need_validation = True
            if isinstance(index, int) and index >= 0:
                loc = cv2helper.npwhere(rlt >= similarity)
                cnt = loc[0].size

                if cnt > 1:
                    distance = min(tplImgHeight, tplImgWidth)
                    logger.debug('found count:%s' % cnt)
                    logger.debug('distance:%s' % distance)

                    tmpPoints = self._getMultiResult(max_loc, loc, distance)
                    logger.debug('distance:%s' % distance)

                    # todo: check whether it is real suitable
                    pts = []
                    for pt in tmpPoints:
                        #                         # phash 验证
                        #                         p1 = pHash(newTplImg.copy())
                        #                         roiImg = cv2helper.roi(scnImg.copy(), (pt[0], pt[1], pt[0]+tplImgWidth, pt[1]+tplImgHeight))
                        #                         p2 = pHash(roiImg)
                        #                         pHM = hamming(p1, p2)
                        #                         logger.debug('pt:%s--hamming distance--:%s' % (str(pt),pHM))
                        #                         # 三通道模板匹配验证
                        #                         matched = self._matchTemplateWithSeperateChannels(newTplImg.copy(), scnImg.copy(), (pt[0],pt[1],0,0))
                        #                         logger.debug('pt:%s--hist check--:%s' % (str(pt),matched))
                        #                         if matched:
                        #                             pts.append(pt)
                        # 直方图验证
                        validation_rlt = self._validate(newTplImg, scnImg, pt)
                        if validation_rlt == 0:
                            pts.append(pt)

                    finalCount = len(pts)
                    if finalCount > index:
                        tmp = pts[index]
                        if tmp == max_loc:
                            need_validation = False
                        max_loc = tmp
                    logger.info('final count:%s' % finalCount)
                    logger.info('index:%s' % index)
                    logger.info('point:%s' % str(max_loc))

            # todo: 找到后需要再次通过直方图确认，如果相似度很高，则不必再验证
            if need_validation and max_val < 0.8:
                if self._validate(newTplImg, scnImg, max_loc, True) > 1:
                    # 很大可能不相似
                    logger.info('not similarity after validation')
                    max_loc = None
        #                     max_val = 0

        rect = None
        if max_loc:
            rect = (max_loc[0], max_loc[1], tplImgWidth, tplImgHeight)
        return (max_val, rect)

    def _roi(self, tpl, img, rc, scaleRatioDelta):
        th, tw = tpl.shape[:2]
        ih, iw = img.shape[:2]
        l, t, w, h = rc
        delta = int(max(th * scaleRatioDelta, tw * scaleRatioDelta, 20)) + 1
        _l = l - delta
        _t = t - delta
        _r = l + w + delta
        _b = t + h + delta
        if _l < 0:
            _l = 0
        if _t < 0:
            _t = 0
        if _r > iw:
            _r = iw - 1
        if _b > ih:
            _b = ih - 1
        newImg = img[_t:_b, _l:_r].copy()
        return (newImg, (_l, _t))

    def _getHistSimilarity(self, tpl, scene, scale, rc):
        if not self._use_histSimilarity:
            return 1000

        tplImgHeight, tplImgWidth = tpl.shape[:2]
        newTplImg = tpl.copy()
        if scale != 1.0:
            tplImgHeight = int(tplImgHeight * scale)
            tplImgWidth = int(tplImgWidth * scale)
            newTplImg = cv2helper.resize(tpl, tplImgWidth, tplImgHeight)

        l, t, w, h = rc
        newSceneImg = scene[t:(t + h), l:(l + w)].copy()

        histSimilarity = self._hist.compare(newTplImg, newSceneImg)
        self._histSimilarity = histSimilarity
        if histSimilarity > self._maxHistSimilarity:
            self._maxHistSimilarity = histSimilarity
        if histSimilarity < self._minHistSimilarity:
            self._minHistSimilarity = histSimilarity
        logger.debug('hist similarity %s'%histSimilarity)
        return histSimilarity

    def _scale_direction(self, templ, image, direction, zoomMax, scale, lastMaxVal, rocPoint):

        logger.debug('scale direction, direction:%s' % direction)
        logger.debug('zoomMax:%s' % zoomMax)
        logger.debug('scale:%s' % scale)
        logger.debug('lastMaxValue:%s' % lastMaxVal)

        rocImage = image.copy()
        tryCount = 0
        while abs(1.0 - scale) < zoomMax:
            if lastMaxVal > self._experienceSimilarity:
                delta = 0.01
            elif lastMaxVal > self._lessGoodSimilarity2:
                delta = 0.02
            else:
                delta = 0.03
            scale = round(scale + direction * delta, 3)

            max_val, rect = self._matchTemplate(templ, rocImage, scale, self._trustSimilarity)
            if rect is None:
                break

            if max_val >= self._lessGoodSimilarity2:
                # 相似度必须大于某一个阈值，直方图比较才作为参考
                histSimilarity = self._getHistSimilarity(templ, image, scale, rect)
                if histSimilarity <= self._histTrustSimilarity:
                    if max_val >= self._experienceSimilarity:
                        # 如果相似度 > experienceSimilarity 并且 直方图比较结果 < histTrustSimilarity， 则认为很相似，直接返回
                        return scale, max_val, self._calcRect(rect, rocPoint)

                    if rocPoint is None:
                        rocImage, rocPoint = self._roi(templ, image, rect, zoomMax)

            time.sleep(0.05)  # 必须加，释放CPU资源
            if max_val < self._trustSimilarity:
                if max_val < lastMaxVal and max_val < self._experienceSimilarity:
                    # 比上次匹配结果更差，但是相似度小于experienceSimilarity
                    tryCount += 1
                    if tryCount > self._badTryCount:
                        break
                else:
                    tryCount = 1
                lastMaxVal = max_val
                continue

            return scale, max_val, self._calcRect(rect, rocPoint)

        return scale, None, None

    def _calcRect(self, rect, rocPoint):
        if rocPoint is None:
            rocPoint = (0, 0)
        l, t, w, h = rect
        x, y = rocPoint
        rect = (l + x, t + y, w, h)
        return rect

    def _scaleMatch(self, templ, image, similarity, maxValue, maxRect, **kwargs):
        lastMaxVal = maxValue

        scale = 1.0
        rocPoint = None
        rocImage = image.copy()
        if maxValue >= self._lessGoodSimilarity2:
            # 相似度必须大于某一个阈值，直方图比较才作为参考
            histSimilarity = self._getHistSimilarity(templ, image, scale, maxRect)
            if histSimilarity <= self._histTrustSimilarity:
                if maxValue >= self._experienceSimilarity:
                    # 如果相似度 > experienceSimilarity 并且 直方图比较结果 < histTrustSimilarity， 则认为很相似，直接返回
                    return scale, maxValue, maxRect

                rocImage, rocPoint = self._roi(templ, image, maxRect, self._zoomOutDelta)

        zoomAttr = {1: [0, 0, 0], -1: [0, 0, 0]}

        if self._zoom == 0:
            # 计算该先往哪方面缩放
            delta = 0.03
            if lastMaxVal > self._experienceSimilarity:
                delta = 0.01
            elif lastMaxVal > self._lessGoodSimilarity2:
                delta = 0.02

            zoom_out_scale = 1.0 + delta
            zoom_out_max_val, zoom_out_rect = self._matchTemplate(templ, rocImage, zoom_out_scale,
                                                                  self._trustSimilarity)
            if zoom_out_rect is None:
                return 1.0, None, None

            if zoom_out_max_val >= self._trustSimilarity:
                return zoom_out_scale, zoom_out_max_val, self._calcRect(zoom_out_rect, rocPoint)

            zoom_in_scale = 1.0 - delta
            zoom_in_max_val, zoom_in_rect = self._matchTemplate(templ, rocImage, zoom_in_scale, self._trustSimilarity)
            if zoom_in_rect is None:
                return 1.0, None, None

            if zoom_in_max_val >= self._trustSimilarity:
                return zoom_in_scale, zoom_out_max_val, self._calcRect(zoom_in_rect, rocPoint)

            zoomAttr[1] = [self._zoomOutDelta, zoom_out_scale, zoom_out_max_val]
            zoomAttr[-1] = [self._zoomInDelta, zoom_in_scale, zoom_in_max_val]
            if zoom_out_max_val >= zoom_in_max_val:
                direction = 1
            else:
                direction = -1

        else:
            direction = self._zoom
            scale = 1.0
            zoomAttr[direction][1] = 1.0
            zoomAttr[direction][2] = lastMaxVal
            if direction == 1:
                zoomAttr[direction][0] = self._zoomOutDelta
            else:
                zoomAttr[direction][0] = self._zoomInDelta

        logger.debug('direction:%s' %direction)
        logger.debug('zoom:%s' % self._zoom)
        logger.debug('zoom attrs:%s' % str(zoomAttr))

        scale, max_val, rect = self._scale_direction(templ, rocImage, direction, zoomAttr[direction][0],
                                                     zoomAttr[direction][1], zoomAttr[direction][2], rocPoint)

        logger.debug('direction:%s' % direction)
        logger.debug('scale:%s' % scale)
        logger.debug('max_val:%s' % max_val)
        logger.debug('rect:%s' % str(rect))

        if rect is not None:
            return scale, max_val, rect

        if self._zoom == 0:
            direction = direction * -1
            scale, max_val, rect = self._scale_direction(templ, rocImage, direction, zoomAttr[direction][0],
                                                         zoomAttr[direction][1], zoomAttr[direction][2], rocPoint)
            if rect is not None:
                return scale, max_val, rect

        return 1.0, None, None

    def _searchImage(self, tplData, sceneData, similarity, **kwargs):
        sceneImg = sceneData.copy()
        position = kwargs.get('position')
        logger.debug('templateImg position:%s' % str(position))
        is_transparent = kwargs.get('is_transparent')
        logger.debug('templateImg is_transparent:%s' % is_transparent)
        if position and len(position) == 4:
            logger.info('TemplateImg position is locked,crop Img!')
            crop_position = _getPosition(tplData, sceneData, position)
            crop_x_min, crop_y_min, crop_x_max, crop_y_max = crop_position
            sceneData = sceneData[crop_y_min:crop_y_max, crop_x_min:crop_x_max]
        else:
            logger.info('TemplateImg position is unlocked')
            crop_x_min, crop_y_min, crop_x_max, crop_y_max = 0, 0, 0, 0


        templ_h, templ_w = tplData.shape[:2]
        sceneImage_h, sceneImage_w = sceneData.shape[:2]

        if templ_h > sceneImage_h or templ_w > sceneImage_w:
            logger.error('tpl image size is smaller than screen' )
            return (None, None)

        res_simpleColor=judge_SimpleColor(tplData)
        scaleRatio = 1.0
        if is_transparent==1 or res_simpleColor:
            sim,rect=transparent(tplData,sceneData)
            if position and len(position) == 4:
                if sim>=0.6:
                    return ((rect[0]+crop_x_min, rect[1]+crop_y_min, rect[0] + rect[2]+crop_x_min, rect[1] + rect[3]+crop_y_min), scaleRatio)
            else:
                if sim>=0.8:
                    return ((rect[0] + crop_x_min, rect[1] + crop_y_min, rect[0] + rect[2] + crop_x_min,
                             rect[1] + rect[3] + crop_y_min), scaleRatio)
        if 'scaleRatio' in kwargs:
            scaleRatio = kwargs.pop('scaleRatio')
            max_val, rect = self._matchTemplate(tplData, sceneData, scaleRatio, similarity)
        else:
            max_val, rect = self._matchTemplate(tplData, sceneData, 1.0, similarity)

        if rect is None:
            return (None, None)

        if max_val < similarity:

            if 'scaleMatch' in kwargs and kwargs['scaleMatch']:
                scaleRatio, max_val, rect = self._scaleMatch(tplData, sceneData, similarity, max_val, rect, **kwargs)
                if rect:
                    x, y, w, h = rect
                    return ((x+crop_x_min, y+crop_y_min, x + w+crop_x_min, y + h+crop_y_min), scaleRatio)
            return (None, None)

        return ((rect[0]+crop_x_min, rect[1]+crop_y_min, rect[0] + rect[2]+crop_x_min, rect[1] + rect[3]+crop_y_min), scaleRatio)


    def searchImage(self, templateImage, sceneImage, similarity=0.7, gray=False, **kwargs):
        result = MatchResult()
        result.method = 'template'
        st = time.time()
        title = ''
        self._reset(similarity, **kwargs)
        tplData = None
        if isinstance(templateImage, str):
            title = os.path.splitext(os.path.split(templateImage)[-1])[0]
            tplData = self._getImageData(templateImage, gray)
        elif cv2helper.isNdarray(templateImage):
            if gray and len(tplData.shape) == 3:
                tplData = cv2helper.cvtColor(templateImage)
            else:
                tplData = templateImage
        else:
            raise TypeError('unknown type:%s' % type(templateImage))


        sceneData = None
        if isinstance(sceneImage, str):
            title = '%s_%s' % (title, os.path.splitext(os.path.split(sceneImage)[-1])[0])
            sceneData = self._getImageData(sceneImage, gray)
        elif cv2helper.isNdarray(sceneImage):
            if gray and len(sceneImage.shape) == 3:
                sceneData = cv2helper.cvtColor(sceneImage)
            else:
                sceneData = sceneImage
        else:
            raise TypeError('unknown type:%s' % type(sceneImage))

        if tplData is None or sceneData is None:
            et = time.time()
            time_cost = et - st
            logger.debug('failed to get image data')
            result.time=time_cost
            result.parameters = kwargs
            return result

        if isinstance(templateImage, str) and int(kwargs.get('cache', '1')) and \
                templateImage in TemplateMatcher._SCALE_RATIO_CACHE:
            kwargs['scaleRatio'] = TemplateMatcher._SCALE_RATIO_CACHE[templateImage]

        rect, scaleRatio = self._searchImage(tplData, sceneData, similarity, **kwargs)
        if rect:
            index = kwargs.get('index', -1)
            if index >= 0:
                logger.debug('index:%s' % index)
                finalSimilarity = self._similarity
                if finalSimilarity > similarity:
                    # 取标准相似度值，否则结果只有1个
                    finalSimilarity = similarity

                _, _rect = self._matchTemplate(tplData, sceneData, scaleRatio, finalSimilarity, index)
                if rect:
                    l, t, w, h = _rect
                    rect = (l, t, l + w, t + h)

            if rect:
                if isinstance(templateImage, str) and int(kwargs.get('cache', '1')) and \
                        scaleRatio != 1.0 and templateImage not in TemplateMatcher._SCALE_RATIO_CACHE:
                    TemplateMatcher._SCALE_RATIO_CACHE[templateImage] = scaleRatio

                if isinstance(templateImage, str):
                    et = time.time()
                    time_cost = et - st
                    logger.debug('found, matched count:%s' % self._matchCount)
                    logger.debug('rect: %s' % str(rect))
                    logger.debug('final scaleRatio:%s' % scaleRatio)
                    logger.debug('max hist:%s' % self._maxHistSimilarity)
                    logger.debug('min similarity:%s' % self._minSimilarity)
                    logger.debug('histSimilarity:%s' % self._histSimilarity)
                    logger.debug('similarity:%s' % self._similarity)
                    logger.debug('time cost:%s' % time_cost)
                    logger.debug('matched count:%s' % self._matchCount)

                if 'showResult' in kwargs and kwargs['showResult']:
                    self._showResult(tplData, sceneData, [rect], "OK_%s" % title)


                result.rect = rect
                et = time.time()
                time_cost = et - st
                result.time = time_cost
                result.scale_ratio = scaleRatio
                result.parameters = kwargs
                return result

        if isinstance(templateImage, str):
            et = time.time()
            time_cost = et - st
            result.time = time_cost
            result.parameters = kwargs
            logger.debug('none, matched count:%s' % self._matchCount)
            logger.debug('rect: %s' % str(rect))
            logger.debug('max hist:%s' % self._maxHistSimilarity)
            logger.debug('min similarity:%s' % self._minSimilarity)
            logger.debug('time cost:%s' % time_cost)
            logger.debug('matched count:%s' % self._matchCount)
        return result

    def _showResult(self, templateData, sceneData, rects, title='show'):
        for rect in rects:
            l, t, r, b = rect
            cv2helper.eval2('cv2.rectangle')(sceneData, (l, t), (r, b), (0, 0, 255), 2)

        h1, w1 = templateData.shape[:2]
        h2, w2 = sceneData.shape[:2]

        if len(sceneData.shape) > 2:
            vis = cv2helper.eval2('np.zeros')((max(h1, h2), w1 + w2, 3))
        else:
            vis = cv2helper.eval2('np.zeros')((max(h1, h2), w1 + w2))

        vis[:h1, :w1] = templateData
        vis[:h2, w1:w1 + w2] = sceneData

        fshow = '%s.jpg' % title
        cv2.imwrite(fshow, vis)
        tmp = cv2.imread(fshow)
        cv2helper.show(tmp, title)
        os.remove(fshow)