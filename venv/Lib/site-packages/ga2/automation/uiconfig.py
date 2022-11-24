import yaml
from ga2.common.loggerConfig import logger
from ga2.device.device import DeviceType
from ga2.automation.by import By


class UIConfig:
    DeviceTypeMapper = {DeviceType.DEVICE_ANDROID: "android", DeviceType.DEVICE_IOS: "ios"}
    defaultConfig = None

    def __init__(self, path):
        self.path = path
        self._version = None
        self._elements = None
        self.load(path)


    @staticmethod
    def get_default():
        return UIConfig.defaultConfig

    @staticmethod
    def set_default(uiconfig):
        UIConfig.defaultConfig = uiconfig

    def set_default(self):
        UIConfig.defaultConfig = self

    def load(self, path):
        data = yaml.safe_load(open(path))
        assert ("elements" in data)
        if "version" in data:
            self._version = data["version"]

        self._elements = data["elements"]


    def get_locator(self, id, device_type):
        device_type_str = UIConfig.DeviceTypeMapper[device_type]
        if id not in self._elements:
            logger.error("id {} is not defined in uiconfig ".format(id))
            return (None, None)
        locators = self._elements[id]
        if isinstance(locators, dict):
            if device_type_str not in locators:
                logger.error("id {}'s locator in {} is not defined in uiconfig ".format(id, device_type))
                return (None, None)
            locators = locators[device_type_str]
        if len(locators) == 0:
            logger.error("id {}'s locator is not defined in uiconfig ".format(id))
            return (None, None)
        if len(locators) == 0:
            logger.error("id {}'s locator is not defined in uiconfig ".format(id))
            return (None, None)
        if len(locators) > 1:
            logger.error("multiple id {}'s locators is  defined in uiconfig. choose the first one for now ".format(id))
            return (None, None)
        locator = locators[0]
        for key in locator.keys():
            method = By.__dict__.get(key)
            params = locator[key]
            return (method, params)
        return (None, None)



