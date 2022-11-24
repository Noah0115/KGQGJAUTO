#-*- coding: UTF-8 -*-

import abc, six
import cv2
from ga2.device.deviceOrientation import DeviceOrientation

@six.add_metaclass(abc.ABCMeta)
class ScreenShoter():

    @abc.abstractmethod
    def screenshot(self, localpath=None, portrait=True, height=None):
        pass

    # @abc.abstractmethod
    # def screenshot_portrait(self, localpath=None, height=None):
    #     pass


    def rotate_to_portrait(self, origin_image, origin_orientation):
        if origin_orientation is DeviceOrientation.PORTRAIT:
            return origin_image
        elif origin_orientation is DeviceOrientation.LANSCAPE:
            return cv2.flip(cv2.transpose(origin_image), 1)
        elif origin_orientation is DeviceOrientation.PORTRAIT_UPSIDEDOWN:
            return cv2.flip(origin_image, -1)
        elif origin_orientation is DeviceOrientation.LANDSCAPERIGHT:
            return cv2.flip(cv2.transpose(origin_image), 0)


