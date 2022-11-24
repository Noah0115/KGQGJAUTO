import abc, six
from enum import Enum
from ga2.common.loggerConfig import logger
from ga2.common.utils import *
from ga2.engine.engineFactory import EngineFactory
from ga2.cloud import platformHelper
from ga2.engine.engine import *


class DeviceType(Enum):
    DEVICE_ANDROID = 0
    DEVICE_IOS = 1


@six.add_metaclass(abc.ABCMeta)
class Device():
    _engine_connector = None
    _device_sdk_port = 27019
    _local_engine_port = None
    _screenshoter = None
    defaultDevice = None

    @staticmethod
    def get_default():
        return Device.defaultDevice

    @staticmethod
    def set_default(device):
        Device.defaultDevice = device

    def set_default(self):
        Device.defaultDevice = self

    @abc.abstractmethod
    def device_type(self):
        pass

    @abc.abstractmethod
    def push(self, local_path, remote_path):
        pass

    @abc.abstractmethod
    def pull(self, remote_path, local_path):
        pass

    @property
    def screenshoter(self):
        return self._screenshoter

    @screenshoter.setter
    def screenshoter(self, shoter):
        self._screenshoter = shoter

    def engine_connector(self):
        if self._engine_connector is None:
            logger.warn("engine connector is none , try to init it ...")
            self.init_engine_sdk()
        return self._engine_connector

    '''
    init engine gautomator sdk(create a valid client to sdk)
    param:  local_engine_port: a free port used to forward to device engine port
            timeout: engine connecting timeout in seconds
            if running in cloud , a free port will be forward instead of the given param
    '''

    @callLog
    def init_engine_sdk(self, engine_type=None, local_engine_port=None, timeout=60):
        if local_engine_port is not None:
            self._local_engine_port = int(os.environ.get("LOCAL_ENGINE_PORT", local_engine_port))
        self._local_engine_port = self._local_engine_port or 53001
        if is_cloud_mode():
            response = platformHelper.get_platform_client().platform_forward(self._device_sdk_port)
            if response is None:
                return ErrType.ERR_CLOUD_PLATFORM
            else:
                self._local_engine_port = response["localPort"]
        else:
            self.forward(self._local_engine_port, self._device_sdk_port)
        counts = int(timeout / 2 + 1)
        origin_engine_type = engine_type
        for i in range(counts):
            try:
                engine_type = engine_type or "Unity3D"  # use default unity to connect and get the real engine type
                self._engine_connector = EngineFactory.create_engine_connector(engine_type, os.environ.get("PLATFORM_IP") if is_cloud_mode() else "127.0.0.1",
                                                                               int(self._local_engine_port))
                if self._engine_connector is None:
                    logger.error("create engine failed . invalid type : " + str(engine_type))
                    return ErrType.ERR_INVALID_ENGINETYPE
                version = self._engine_connector.get_sdk_version()
                if version:
                    logger.debug(version)
                    if origin_engine_type is None:
                        engine_type = EngineFactory.recognize_engine_type(version)
                        if engine_type is None:
                            logger.error("create engine failed . unrecognized engine type.")
                            return ErrType.ERR_INVALID_ENGINETYPE
                        logger.debug("engine type recognized: " + engine_type)
                        self._engine_connector = EngineFactory.create_engine_connector(engine_type, os.environ.get("PLATFORM_IP") if is_cloud_mode() else "127.0.0.1",
                                                                                       int(self._local_engine_port))
                    return ErrType.ERR_SUCCEED
            except Exception as e:
                time.sleep(2)
        logger.error("init engine sdk timeout")
        return ErrType.ERR_CONNECT_TO_SDK_FAILED

    @abc.abstractmethod
    def forward(self, local_port, remote_port):
        pass

    @abc.abstractmethod
    def remove_forward(self, local_port):
        pass

    @abc.abstractmethod
    def get_top_app(self):
        pass

    @abc.abstractmethod
    def launch_app(self, appid, activity=None, timeout=60, alert_handler=None):
        pass

    def kill_app(self, app):
        pass

    @callLog
    def screenshot(self, localpath=None, portrait=True, height=None):
        return self._screenshoter.screenshot(localpath , portrait , height)

    @abc.abstractmethod
    def display_size(self):
        pass

    @abc.abstractmethod
    def orientation(self):
        pass

    @abc.abstractmethod
    def home(self):
        pass

    @abc.abstractmethod
    def text(self, content):
        pass


    @abc.abstractmethod
    def touch(self, x, y):
        pass



    @abc.abstractmethod
    def double_touch(self, x, y):
        pass

    @abc.abstractmethod
    def long_press(self, x, y, duration=2):
        pass

    @abc.abstractmethod
    def drag(self, sx, sy, dx, dy, duration=1):
        pass

    @abc.abstractmethod
    def clear_app(self, appid):
        logger.info("ios clear_app : unimplemented yet")

    @abc.abstractmethod
    def keyevent(self, keycode):
        logger.info("keyevent : unimplemented yet")



    # '''
    # touch the center of the given rectangle bound.
    # param: bound: a list as [s,y,width,height].
    # '''
    # def __touch_bound(self, bound):
    #     if 0 < bound[0] < 1 and 0 < bound[1] < 1 and 0 < bound[2] < 1 and 0 < bound[3] < 1:
    #         display_size = self.display_size()
    #         bound[0] *= display_size[0]
    #         bound[1] *= display_size[1]
    #         bound[2] *= display_size[0]
    #         bound[3] *= display_size[1]
    #     x, y = bound[0] + bound[2] / 2, bound[1] + bound[3] / 2
    #     self.touch(x, y)
    #
    # def __touch_hold_bound(self, bound, duration=1.5):
    #     if 0 < bound[0] < 1 and 0 < bound[1] < 1 and 0 < bound[2] < 1 and 0 < bound[3] < 1:
    #         display_size = self.display_size()
    #         bound[0] *= display_size[0]
    #         bound[1] *= display_size[1]
    #         bound[2] *= display_size[0]
    #         bound[3] *= display_size[1]
    #     x, y = bound[0] + bound[2] / 2, bound[1] + bound[3] / 2
    #     self.long_press(x, y, duration)





