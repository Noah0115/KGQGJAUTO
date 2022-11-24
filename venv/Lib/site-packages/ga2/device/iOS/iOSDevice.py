# -*- coding: UTF-8 -*-
import re
from ga2.device.device import Device
from ga2.device.device import DeviceType
from ga2.device.deviceOrientation import *
from ga2.device.iOS.iMobiledevice import IMobileDevice
from ga2.device.iOS.defaultScreenShoter import DefaultScreenshoter
from ga2.device.iOS.wdaManager import WdaManager
from ga2.device.iOS.iProxyManager import IProxyManager
from ga2.common.loggerConfig import logger
from ga2.common.cmdExecuter import CmdExecuter
from ga2.common.utils import *
import atexit


class IOSDevice(Device):
    '''
    param: wdaport: the local port you have forward to the device
    '''

    def __init__(self, udid,  gaport=None, screenshoter=None):
        if udid is None or udid is "":
            dev_list = IMobileDevice.get_device_list()
            assert (len(dev_list) > 0)
            udid = dev_list[0].decode("utf-8")
        self.imobile_cmder = IMobileDevice(udid)
        self.__iproxy = IProxyManager(udid)
        self._engine_connector = None
        self.__wda_connector = None
        self._local_engine_port = gaport

        def __get_wdaport_by_udid(udid):
            outputlines = CmdExecuter.execute_and_wait("ps -ef|grep \"iproxy [0-9]\+ 8100 " + udid + "\"")
            for line in outputlines:
                ret = re.search("iproxy ([0-9]+) 8100 " + udid, line.decode("utf-8"))
                if ret:
                    return ret.group(1)
            outputlines = CmdExecuter.execute_and_wait("ps -ef|grep \"iproxy [0-9]\+ 8100" + "\"")
            for line in outputlines:
                ret = re.search("iproxy ([0-9]+) 8100$", line.decode("utf-8"))
                if ret:
                    return ret.group(1)
            logger.warn("No wda port detected for device.. " + udid)
            return None

        wdaport = os.environ.get("WDA_LOCAL_PORT", __get_wdaport_by_udid(udid))
        if wdaport:
            logger.info("wda port detected: " + wdaport)
            self.__wda_connector = WdaManager(wdaport, os.environ.get("PLATFORM_IP", "127.0.0.1"))
        else:
            logger.warn("wda port is not set!!")
        self._screenshoter = screenshoter or DefaultScreenshoter(self.__wda_connector)
        atexit.register(self.__cleanup)
        pass

    def wda_session(self):
        if self.__wda_connector == None:
            logger.error("wda connector is not inited... plsease make sure wda is connectable")
        return self.__wda_connector.get_session()

    def __cleanup(self):
        if self.__iproxy:
            self.__iproxy.remove_all_forwards()


    '''
    params: appfile:path to .ipa file
    '''

    # def install(self,appfile):
    #     self.imobile_cmder.install(appfile)
    #
    # def uninstall(self,appid):
    #     self.imobile_cmder.uninstall(appid)

    def device_type(self):
        return DeviceType.DEVICE_IOS


    @callLog
    def launch_app(self, appid, activity=None, timeout=60, alert_handler=None):
        if self.__wda_connector is None:
            logger.error("wda connector is not inited... plsease make sure wda is connectable")
            return ErrType.ERR_WDA_NOT_RUNNING
        session = self.__wda_connector.new_session(bundleid=appid)
        alert_handler = alert_handler or self.__default_alert_callback
        start_time = time.time()
        for i in range(0, int(timeout/3)):
            cur_top_app = self.get_top_app()
            logger.debug("current top app is :" + cur_top_app + "target is: " + appid)
            if cur_top_app != appid:
                alert_handler(session)
            else:
                break
            time.sleep(3)
            if time.time() - start_time > timeout:
                logger.warn("launch_app timeout...")
                return ErrType.ERR_TIMEOUT
        return ErrType.ERR_SUCCEED

    def start_alert_handler(self, handler=None):
        if self.__wda_connector is None:
            logger.error("wda connector is not inited... plsease make sure wda is connectable")
            return ErrType.ERR_WDA_NOT_RUNNING
        handler = handler or self.__default_alert_callback
        logger.info("setting alert handler...")
        self.__wda_connector.get_session().set_alert_callback(handler)
        return ErrType.ERR_SUCCEED

    def __default_alert_callback(self, session):
        btns = set([u'稍后', u'稍后提醒我', u'不再提醒', u'无线局域网与蜂窝移动网络', u'允许', u'知道了', u'确定', u'好']).intersection(
            session.alert.buttons())
        if len(btns) == 0:
            logger.warn("Alert  not handled, buttons: " + ', '.join(session.alert.buttons()))
            return
        logger.info('alert handled：' + str(list(btns)[0]))
        session.alert.click(list(btns)[0])
        pass

    @callLog
    def get_top_app(self):
        if self.__wda_connector is None:
            logger.error("wda connector is not inited... plsease make sure wda is connectable")
            return None
        return self.__wda_connector.get_top_bundleid()

    # @callLog
    # def foreground(self,appid):
    #     self.wda_connector.get_session(appid).activate(1)

    '''
    For now , just kill the app launched by device interface. It's better to save a map as {appid:session}
    '''

    @callLog
    def kill_app(self, appid=None):
        self.__wda_connector.close_session(appid)

    @callLog
    def home(self):
        self.__wda_connector.wda_client.home()

    def forward(self, local_port, remote_port):
        self.__iproxy.forward(localport=local_port, remoteport=remote_port)

    def remove_forward(self, local_port):
        self.__iproxy.remove_forward(localport=local_port)

    '''
    input text to device
    param : str
    '''

    def text(self, content):
        self.__wda_connector.get_session().send_keys(content)

    '''
    get the current device display size
    return: two values  (width,height)
    '''

    def display_size(self):
        return self.__wda_connector.get_session().window_size()

    '''
    get the current device orientation
    return: enum DeviceOrientation value
    '''

    def orientation(self):
        return WDA_ORIENTATION_MAP[self.__wda_connector.get_session().orientation]

    '''
    touch at the given position 
    param: x,y : pixel pos  or rate of the current device screen.
    '''

    def touch(self, x, y):
        if 0 < x < 1 and 0 < y < 1:
            display_size = self.display_size()
            x = x * display_size[0]
            y = y * display_size[1]
        logger.info("tap :" + str(x) + str(y))
        self.__wda_connector.get_session().tap(x, y)

    '''
    double touch at the given position 
    param: x,y : pixel pos  or rate of the current device screen.
    '''

    def double_touch(self, x, y):
        if 0 < x < 1 and 0 < y < 1:
            display_size = self.display_size()
            x = x * display_size[0]
            y = y * display_size[1]
        self.__wda_connector.get_session().double_tap(x, y)

    '''
    note:  the param "duration" indicates the touchdown and hold time rather than the moving time.
    param: sx,sy,dx,dy: start and end pixel pos  or rate of the current device screen.
           duration: start coordinate press duration in seconds
    '''

    def drag(self, sx, sy, dx, dy, duration=0.3):
        if 0 < sx < 1 and 0 < sy < 1 and 0 < dx < 1 and 0 < dy < 1:
            display_size = self.display_size()
            sx = sx * display_size[0]
            sy = sy * display_size[1]
            dx = dx * display_size[0]
            dy = dy * display_size[1]
        self.__wda_connector.get_session().swipe(sx, sy, dx, dy, duration)

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
        self.__wda_connector.get_session().tap_hold(x, y, duration)


    def push(self, local_path, remote_path):
        logger.error("ios push unimplemented yet")
        return ErrType.ERR_UNIMPLEMENTED

    def pull(self, remote_path, local_path):
        logger.error("ios pull unimplemented yet")
        return ErrType.ERR_UNIMPLEMENTED

    def clear_app(self):
        logger.error("ios clear_app unimplemented yet")
        return ErrType.ERR_UNIMPLEMENTED

    def keyevent(self):
        logger.error("ios keyevent unimplemented yet")
        return ErrType.ERR_UNIMPLEMENTED

    click = touch
    swipe = drag