# -*- coding: UTF-8 -*-

from ga2.device.device import Device
from ga2.device.device import DeviceType
from ga2.device.deviceOrientation import DeviceOrientation
from ga2.common.loggerConfig import logger
from ga2.device.android.inputHelper import InputHeler
from ga2.common.utils import *
from ga2.device.android.adbProcess import *
from ga2.device.android.uiauto.uiautoManager import UiautoManager
from ga2.device.android.defaultScreenShoter import DefaultScreenshoter
from ga2.cloud import platformHelper
import atexit


class AndroidDevice(Device):

    def __init__(self, serial, need_uiauto=True, uiautoport=None, gaport=None, screenshoter=None):
        self.uiauto_man = UiautoManager(serial, os.environ.get("PLATFORM_IP", "127.0.0.1"), port=uiautoport) if need_uiauto else None
        self._serial = serial
        self._local_engine_port = gaport
        self._screenshoter = screenshoter or DefaultScreenshoter(serial, self.uiauto_man)
        atexit.register(self.__cleanup)
        self.__forward_list = []
        pass

    def __cleanup(self):  #clean forward list ?
        for port in self.__forward_list:
            self.remove_forward(port)

    def device_type(self):
        return DeviceType.DEVICE_ANDROID

    '''
       :param package:
       :return: errorcode
       :note: app will not be relaunched if not being foreground
    '''
    @callLog
    def launch_app(self, package, activity=None, timeout=60, alert_handler=None):
        activity = activity or os.environ.get("LAUNCHACTIVITY", "android.intent.category.LAUNCHER")
        if is_cloud_mode():
            if platformHelper.get_platform_client().launch_app(package, activity) is True:
                return ErrType.ERR_SUCCEED
        adb_wait("shell monkey -p " + package + " -c " + activity + " 1", self._serial)
        pid = adb_get_pid_by_name(package)

        return ErrType.ERR_SUCCEED if pid is not None and pid > 0 else ErrType.ERR_PROCESS_NOT_FOUND

    def get_top_app(self):
        package = adb_get_top_app(self._serial)
        if package is None and self.uiauto_man:
            package = self.uiauto_man.ui_device.info["currentPackageName"]
            if package:
                logger.debug("found top package by uiauto = {0}".format(package))
        return package

    '''
    kill app by packagename
    '''
    @callLog
    def kill_app(self, appid=None):
        if appid is not None:
            adb_wait("shell am force-stop " + appid, self._serial)

    '''
    clear app data by packagename
    '''
    def clear_app(self, appid):
        cmd = "shell pm clear {0}".format(appid)
        adb_wait(cmd, self._serial)

    @callLog
    def home(self):
        return self.keyevent(keycode=3)

    def keyevent(self, keycode):
        out, err = adb_wait('shell input keyevent ' + str(keycode), self._serial)
        return ErrType.ERR_SUCCEED if err == "" or err is None else ErrType.ERR_ADB

    def forward(self, local_port, remote_port):
        out, err = adb_forward(local_port, remote_port, self._serial)
        if err is not None and len(err) > 0:
            return ErrType.ERR_ADB
        self.__forward_list.append(local_port)
        return ErrType.ERR_SUCCEED

    def remove_forward(self, local_port):
        out, err = adb_remove_forward(local_port, self._serial)
        if err is not None and len(err) > 0:
            return ErrType.ERR_ADB
        self.__forward_list.remove(local_port)
        return ErrType.ERR_SUCCEED

    def push(self, local_path, remote_path):
        out, err = adb_push(local_path, remote_path, self._serial)
        return ErrType.ERR_SUCCEED if err == "" or err is None else ErrType.ERR_ADB

    def pull(self, remote_path,local_path):
        out, err = adb_pull(remote_path, local_path,self._serial)
        return ErrType.ERR_SUCCEED if err == "" or err is None else ErrType.ERR_ADB

    '''
    input text to device
    param : str
    '''
    def text(self, content):
        InputHeler.input_text(text=content, need_one_by_one=True, serial=self._serial)

    '''
    get the current device display size
    in android , there are two kinds of  display_size (screen display_size and app display_size)
    this method will return the current display size got by adb, which may not  equals to the value got by uiautomator
    return: two values  (width,height)
    '''
    def display_size(self):
        return adb_get_display_size(self._serial)

    '''
    get the current device orientation
    return: enum DeviceOrientation value
    '''
    def orientation(self):
        return DeviceOrientation(self.uiauto_man.ui_device.info["displayRotation"])#0,1,2,3

    '''
    touch at the given position 
    param: x,y : pixel pos  or rate of the current device screen.
    '''
    def touch(self, x, y):
        if 0 < x < 1 and 0 < y < 1:
            display_size = self.display_size()
            x = x * display_size[0]
            y = y * display_size[1]
        adb_wait('shell input tap ' + str(x) + ' ' + str(y), self._serial)

    '''
    double touch at the given position 
    param: x,y : pixel pos  or rate of the current device screen.
    '''
    def double_touch(self, x, y):
        logger.error("double_touch unimplemented yet in AndroidDevice")

    '''
    note:  the param "duration" indicates the moving time(seconds).
    param: sx,sy,dx,dy: start and end pixel pos  or rate of the current device screen.
           duration: ms
    '''
    def drag(self, sx, sy, dx, dy, duration=0.3):
        if 0 < sx < 1 and 0 < sy < 1 and 0 < dx < 1 and 0 < dy < 1:
            display_size = self.display_size()
            sx = sx * display_size[0]
            sy = sy * display_size[1]
            dx = dx * display_size[0]
            dy = dy * display_size[1]
        adb_wait('shell input swipe  ' + str(round(sx, 2)) + ' ' + str(round(sy, 2)) + ' ' + str(round(dx, 2)) + ' ' + str(round(dy, 2)) + ' ' + str(int(duration*1000)), self._serial)

    '''
    touch and hold for duration at the given position
    param : x,y : pixel pos  or rate of the current device screen.
            duration: holding seconds
    '''
    def long_press(self, x, y, duration=1.5):
        if 0 < x < 1 and 0 < y < 1:
            display_size = self.display_size()
            x *= display_size[0]
            y *= display_size[1]
        adb_wait('shell input swipe  ' + str(round(x, 2)) + ' ' + str(round(y, 2)) + ' ' + str(round(x+0.1, 2)) + ' ' + str(round(y+0.1, 2)) + ' ' +  str(int(duration*1000)),

                 self._serial)


    click = touch
    swipe = drag
