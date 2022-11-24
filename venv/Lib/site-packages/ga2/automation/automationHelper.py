from ga2.automation.by import By
from ga2.common.loggerConfig import logger
from ga2.common.utils import callLog
from ga2.device.device import Device
from ga2.common.utils import *
from ga2.cloud.reporter import Reporter
from ga2.automation.uiconfig import UIConfig
from ga2.common.WebDriverWait import WebDriverWait
from ga2.automation.automationHelperEngine import AutomationHelperEngine
from ga2.automation.automationHelperNative import AutomationHelperNative
from ga2.automation.automationHelperImage import AutomationHelperImage


class AutomationHelper:

    touch_method_map = {By.NAME_IN_ENGINE: AutomationHelperEngine.handle_element_by_name,
                        By.PATH_IN_ENGINE: AutomationHelperEngine.handle_element_by_path,
                        By.TEXT_NATIVE: AutomationHelperNative.handle_element_by_text,
                        By.CONDITIONS_NATIVE: AutomationHelperNative.handle_element_by_conditions,
                        By.IMAGE_TEMPLATE: AutomationHelperImage.handle_element_by_image_template,
                        By.ELEMENT_IN_ENGINE: AutomationHelperEngine.handle_element_by_self}
    # double_touch_method_map = {By.NAME_IN_ENGINE: AutomationHelperEngine.handle_element_by_name,
    #                            By.PATH_IN_ENGINE: AutomationHelperEngine.handle_element_by_path,
    #                            By.TEXT_NATIVE: AutomationHelperNative.handle_element_by_text,
    #                            By.CONDITIONS_NATIVE: AutomationHelperNative.handle_element_by_conditions,
    #                            By.IMAGE_TEMPLATE: AutomationHelperImage.handle_element_by_image_template,
    #                            By.ELEMENT_IN_ENGINE: AutomationHelperEngine.handle_element_by_self}
    long_press_method_map = {By.NAME_IN_ENGINE: AutomationHelperEngine.handle_element_by_name,
                             By.PATH_IN_ENGINE: AutomationHelperEngine.handle_element_by_path,
                             By.TEXT_NATIVE: AutomationHelperNative.handle_element_by_text,
                             By.CONDITIONS_NATIVE: AutomationHelperNative.handle_element_by_conditions,
                             By.IMAGE_TEMPLATE: AutomationHelperImage.handle_element_by_image_template,
                             By.ELEMENT_IN_ENGINE: AutomationHelperEngine.handle_element_by_self}
    wait_method_map = {By.NAME_IN_ENGINE: AutomationHelperEngine.wait_element_by_name,
                       By.PATH_IN_ENGINE: AutomationHelperEngine.wait_element_by_path,
                       By.TEXT_NATIVE: AutomationHelperNative.wait_element_by_text,
                       By.CONDITIONS_NATIVE: AutomationHelperNative.wait_element_by_conditions,
                       By.IMAGE_TEMPLATE: AutomationHelperImage.wait_element_by_image_template
                       }

    get_bound_map = {By.NAME_IN_ENGINE: AutomationHelperEngine.get_bound_by_name,
                       By.PATH_IN_ENGINE: AutomationHelperEngine.get_bound_by_path,
                       By.ELEMENT_IN_ENGINE: AutomationHelperEngine.get_bound_by_self,
                       By.TEXT_NATIVE: AutomationHelperNative.get_bound_by_text,
                       By.CONDITIONS_NATIVE: AutomationHelperNative.get_bound_by_conditions,
                       By.ELEMENT_NATIVE: AutomationHelperNative.get_bound_by_self
                       }
    wait_list_method_map = {By.PATH_IN_ENGINE: AutomationHelperEngine.wait_elements_by_path}


    # By.ID_IN_UICONFIG: AutomationHelper.wait_element_by_uiconfig}

    @staticmethod
    @callLog
    def wait_element(method, param, timeout, device=None):
        device = device or Device.get_default()
        if not device:
            logger.error("device is not set in automationAPI")
            return None
        if method == By.ID_IN_UICONFIG:
            uiconfig = UIConfig.get_default()
            if uiconfig == None:
                return None
            (method, param) = uiconfig.get_locator(param, device.device_type())
        if method not in AutomationHelper.wait_method_map:
            logger.error("invalid find method :" + str(method))
            return None
        return AutomationHelper.wait_method_map.get(method)(device, param, timeout)

    @staticmethod
    @callLog
    def wait_elements(method, param, timeout, device=None):
        device = device or Device.get_default()
        if not device:
            logger.error("device is not set in automationAPI")
            return None
        if method == By.ID_IN_UICONFIG:
            uiconfig = UIConfig.get_default()
            if uiconfig == None:
                return None
            (method, param) = uiconfig.get_locator(param, device.device_type())
        if method not in AutomationHelper.wait_method_map:
            logger.error("invalid find method :" + str(method))
            return None
        return AutomationHelper.wait_list_method_map.get(method)(device, param, timeout)

    @staticmethod
    @callLog
    def touch_element(method, param, device=None, sleep_after=0.5):
        device = device or Device.get_default()
        if not device:
            logger.error("device is not set in automationAPI")
            return None
        if method == By.ID_IN_UICONFIG:
            uiconfig = UIConfig.get_default()
            if uiconfig == None:
                return None
            (method, param) = uiconfig.get_locator(param, device.device_type())

        if method not in AutomationHelper.touch_method_map:
            logger.error("invalid touch method :" + str(method))
            return None
        ret = AutomationHelper.touch_method_map.get(method)(device, param, device.touch)
        if ret and sleep_after and sleep_after>0:
            time.sleep(sleep_after)
        return ret

    @staticmethod
    @callLog
    def long_press_element(method, param, duration=2, device=None, sleep_after=0.5):
        device = device or Device.get_default()
        if not device:
            logger.error("device is not set in automationAPI")
            return None
        if method == By.ID_IN_UICONFIG:
            uiconfig = UIConfig.get_default()
            if uiconfig == None:
                return None
            (method, param) = uiconfig.get_locator(param, device.device_type())
        if method not in AutomationHelper.long_press_method_map:
            logger.error("invalid long_press method :" + method)
            return None
        ret = AutomationHelper.long_press_method_map.get(method)(device, param, device.long_press, duration=duration)
        if ret and sleep_after and sleep_after>0:
            time.sleep(sleep_after)
        return ret

    @staticmethod
    @callLog
    def get_element_bound(method, param,device=None):
        device = device or Device.get_default()
        if not device:
            logger.error("device is not set in automationAPI")
            return None
        if method == By.ID_IN_UICONFIG:
            uiconfig = UIConfig.get_default()
            if uiconfig == None:
                return None
            (method, param) = uiconfig.get_locator(param, device.device_type())
        if method not in AutomationHelper.get_bound_map:
            logger.error("invalid get_bound_method :" + method)
            return None
        return  AutomationHelper.get_bound_map.get(method)(device, param)


    # @staticmethod
    # @callLog
    # def double_touch_element(method, param, device=None, sleep_after=0.5):
    #     device = device or Device.get_default()
    #     if not device:
    #         logger.error("device is not set in automationAPI")
    #         return None
    #     if method == By.ID_IN_UICONFIG:
    #         uiconfig = UIConfig.get_default()
    #         if uiconfig == None:
    #             return None
    #         (method, param) = uiconfig.get_locator(param, device.device_type())
    #     if method not in AutomationHelper.double_touch_method_map:
    #         logger.error("invalid double touch touch method :" + method)
    #         return None
    #     ret = AutomationHelper.long_press_method_map.get(method)(device, param, device.double_touch)
    #     if ret and sleep_after and sleep_after > 0:
    #         time.sleep(sleep_after)
    #     return ret