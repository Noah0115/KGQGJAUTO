# -*- coding: UTF-8 -*-

import cv2
from ga2.common.utils import callLog
from ga2.device.deviceOrientation import *
from ga2.device.screenShoter import ScreenShoter
import numpy

class DefaultScreenshoter(ScreenShoter):

    def __init__(self, wdaconnector ):
        self.__wda_connector = wdaconnector

    @callLog
    def screenshot(self, localpath=None, portrait=True, height=None):

        pngdata = self.__wda_connector.wda_client.screenshot(localpath)
        pngarr = numpy.fromstring(pngdata, numpy.uint8)
        origin_image = cv2.imdecode(pngarr, cv2.IMREAD_UNCHANGED)
        scaled_image = self.resize_screenshot(origin_image, height) if height else origin_image
        scaled_width, scaled_height = scaled_image.shape[1], scaled_image.shape[0]
        rotated_image = scaled_image
        if portrait:
            orientation = self.__wda_connector.get_session().orientation
            orientation = WDA_ORIENTATION_MAP[orientation]
            if orientation == (
                    DeviceOrientation.LANDSCAPERIGHT or orientation == DeviceOrientation.LANSCAPE) and scaled_height > scaled_width:  # in case the origin picture is  portrait
                orientation = DeviceOrientation.PORTRAIT
            rotated_image = self.rotate_to_portrait(scaled_image, orientation)
        if localpath:
            cv2.imwrite(filename=localpath, img=rotated_image)
        return rotated_image

    def resize_screenshot(self, origin, length):
        if length is None:
            return origin
        display_size = self.__wda_connector.get_session().window_size()
        if display_size[0] > display_size[1]:
            width = int(length * display_size[1] / display_size[0])
            return cv2.resize(origin, (length, width))
        else:
            width = int(length * display_size[0] / display_size[1])
            return cv2.resize(origin, (width, length))


