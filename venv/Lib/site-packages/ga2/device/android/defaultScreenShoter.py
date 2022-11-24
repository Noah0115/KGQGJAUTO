# -*- coding: UTF-8 -*-

import cv2
from ga2.common.utils import callLog
from ga2.device.android.adbProcess import *
from ga2.device.deviceOrientation import *
from ga2.device.screenShoter import ScreenShoter


class DefaultScreenshoter(ScreenShoter):

    def __init__(self, serial, uiauto_man):
        self._serial = serial
        self.uiauto_man = uiauto_man

    @callLog
    def screenshot(self, localpath=None, portrait=True, height=None):
        cmd = "shell screencap -p /sdcard/screen.png"
        adb_wait(cmd, self._serial)
        origin_image=None
        if localpath:
            adb_pull("/sdcard/screen.png", localpath, self._serial)
            origin_image = cv2.imread(localpath)
        else:
            adb_pull("/sdcard/screen.png", ".", self._serial)
            origin_image = cv2.imread("screen.png")
        scaled_image = self.resize_screenshot(origin_image, height) if height else origin_image
        scaled_width, scaled_height = scaled_image.shape[1], scaled_image.shape[0]
        assert(self.uiauto_man)
        rotated_image = scaled_image
        if portrait:
            orientation = DeviceOrientation(self.uiauto_man.ui_device.info["displayRotation"])
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
        display_size = adb_get_display_size(self._serial)
        if display_size[0] > display_size[1]:
            width = int(length * display_size[1] / display_size[0])
            return cv2.resize(origin, (length, width))
        else:
            width = int(length * display_size[0] / display_size[1])
            return cv2.resize(origin, (width, length))

