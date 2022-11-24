from ga2.common.loggerConfig import logger
from ga2.common.utils import callLog
from ga2.device.device import Device
from ga2.device.android.uiauto import uiautoManager
from ga2.device.android import androidDevice
from ga2.device.device import DeviceType
from ga2.common.utils import *
from ga2.cloud.reporter import Reporter
from ga2.common.WebDriverWait import WebDriverWait


class AutomationHelperNative:

    @staticmethod
    def __get_uiauto_elem_by_text(device, text):
        elem = device.uiauto_man.ui_device(text=text)
        if not elem.exists:
            elem = device.uiauto_man.ui_device(description=text)
        return elem if elem.exists else None

    @staticmethod
    def __get_ios_elem_by_text(device, text):
        session = device.wda_session()
        elem = session(name=text)
        if not elem.exists:
            elem = session(label=text)
            if not elem.exists:
                elem = session(value=text)
        return elem if elem.exists else None

    @staticmethod
    def __get_uiauto_elem_by_conditions(device, conditions):
        elem = device.uiauto_man.ui_device(**conditions)
        return elem if elem.exists else None

    @staticmethod
    def __get_ios_elem_by_conditions(device, conditions):
        session = device.wda_session()
        elem = session(**conditions)
        return elem if elem.exists else None

    @staticmethod
    def wait_element_by_conditions(device, conditions, timeout):
        if device:
            element = None
            find_method = None
            if device.device_type() == DeviceType.DEVICE_ANDROID:
                if device.uiauto_man == None:
                    logger.error("wait_element_by_text failed : uiauto_man is not set")
                    return None
                find_method = AutomationHelperNative.__get_uiauto_elem_by_conditions
            elif device.device_type() == DeviceType.DEVICE_IOS:
                session = device.wda_session()
                if session is None:
                    logger.error("wait_element_by_text failed : session is not set")
                    return None
                find_method = AutomationHelperNative.__get_ios_elem_by_conditions
            try:
                element = WebDriverWait(timeout, 2).until(find_method, device, conditions)
            except Exception as e:
                logger.warn("element wait timeout:" + str(conditions))
            return element
        return None

    @staticmethod
    def wait_element_by_text(device, text, timeout):
        if device:
            element = None
            find_method = None
            if device.device_type() == DeviceType.DEVICE_ANDROID:
                if device.uiauto_man == None:
                    logger.error("wait_element_by_text failed : uiauto_man is not set")
                    return None
                find_method = AutomationHelperNative.__get_uiauto_elem_by_text
            elif device.device_type() == DeviceType.DEVICE_IOS:
                session = device.wda_session()
                if session is None:
                    logger.error("wait_element_by_text failed : session is not set")
                    return None
                find_method = AutomationHelperNative.__get_ios_elem_by_text
            try:
                element = WebDriverWait(timeout, 2).until(find_method, device, text)
            except Exception as e:
                logger.warn("element wait timeout:" + text)
            return element
        return None

    @staticmethod
    def handle_element_by_text(device, text, operator, **kwargs):
        if not device:
            return None
        target_pos = None
        if device.device_type() == DeviceType.DEVICE_ANDROID:
            if device.uiauto_man == None:
                logger.error("handle_element_by_text failed : uiauto_man is not set")
                return None
            elem = AutomationHelperNative.__get_uiauto_elem_by_text(device, text)
            if elem:
                bound_info = elem.info[u'bounds']
                left, top, right, bottom = bound_info[u'left'], bound_info[u'top'], bound_info[u'right'], bound_info[
                    u'bottom']
                target_pos = ((left + right) / 2, (top + bottom) / 2)

        elif device.device_type() == DeviceType.DEVICE_IOS:
            session = device.wda_session()
            if session is None:
                logger.error("wait_element_by_text failed : session is not set")
                return None
            elem = AutomationHelperNative.__get_ios_elem_by_text(device, text)
            if elem:
                rect = elem.bound
                target_pos = (rect.x + rect.width / 2, rect.y + rect.height / 2)

        if target_pos:
            if is_cloud_mode():
                (width, height) = device.display_size()
                Reporter().screenshot_with_mark(width, height, target_pos[0], target_pos[1])

            operator(target_pos[0], target_pos[1], **kwargs)
        else:
            logger.warn("native elem not found : " + text)
        return target_pos

    @staticmethod
    def handle_element_by_conditions(device, conditions, operator, **kwargs):
        if not device:
            return None
        target_pos = None
        if device.device_type() == DeviceType.DEVICE_ANDROID:
            if device.uiauto_man == None:
                logger.error("handle_element_by_conditions failed : uiauto_man is not set")
                return None
            elem = AutomationHelperNative.__get_uiauto_elem_by_conditions(device, conditions)
            if elem:
                bound_info = elem.info[u'bounds']
                left, top, right, bottom = bound_info[u'left'], bound_info[u'top'], bound_info[u'right'], bound_info[
                    u'bottom']
                target_pos = ((left + right) / 2, (top + bottom) / 2)

        elif device.device_type() == DeviceType.DEVICE_IOS:
            session = device.wda_session()
            if session is None:
                logger.error("wait_element_by_text failed : session is not set")
                return None
            elem = AutomationHelperNative.__get_ios_elem_by_conditions(device, conditions)
            if elem:
                rect = elem.bound
                target_pos = (rect.x + rect.width / 2, rect.y + rect.height / 2)

        if target_pos:
            if is_cloud_mode():
                (width, height) = device.display_size()
                Reporter().screenshot_with_mark(width, height, target_pos[0], target_pos[1])

            operator(target_pos[0], target_pos[1], **kwargs)
        else:
            logger.warn("native elem not found : " + str(conditions))
        return target_pos

    @staticmethod
    def get_bound_by_conditions(device, conditions):
        if not device:
            return None
        target_pos = None
        if device.device_type() == DeviceType.DEVICE_ANDROID:
            if device.uiauto_man == None:
                logger.error("handle_element_by_conditions failed : uiauto_man is not set")
                return None
            elem = AutomationHelperNative.__get_uiauto_elem_by_conditions(device, conditions)
            if elem:
                bound_info = elem.info[u'bounds']
                left, top, right, bottom = bound_info[u'left'], bound_info[u'top'], bound_info[u'right'], bound_info[
                    u'bottom']
                return (left, top, right, bottom)

        elif device.device_type() == DeviceType.DEVICE_IOS:
            session = device.wda_session()
            if session is None:
                logger.error("wait_element_by_text failed : session is not set")
                return None
            elem = AutomationHelperNative.__get_ios_elem_by_conditions(device, conditions)
            if elem:
                rect = elem.bound
                return (rect.x, rect.y, rect.x + rect.width, rect.y + rect.height)
        return None


    @staticmethod
    def get_bound_by_self(device, element):
        if not device:
            return None
        if not element:
            return None
        target_pos = None
        if device.device_type() == DeviceType.DEVICE_ANDROID:
            bound_info = element.info[u'bounds']
            left, top, right, bottom = bound_info[u'left'], bound_info[u'top'], bound_info[u'right'], bound_info[
                u'bottom']
            return (left, top, right, bottom)

        elif device.device_type() == DeviceType.DEVICE_IOS:
            rect = element.bound
            return (rect.x, rect.y, rect.x + rect.width, rect.y + rect.height)
        return None


    @staticmethod
    def get_bound_by_text(device, text):
        if not device:
            return None
        target_pos = None
        if device.device_type() == DeviceType.DEVICE_ANDROID:
            if device.uiauto_man == None:
                logger.error("handle_element_by_text failed : uiauto_man is not set")
                return None
            elem = AutomationHelperNative.__get_uiauto_elem_by_text(device, text)
            if elem:
                bound_info = elem.info[u'bounds']
                left, top, right, bottom = bound_info[u'left'], bound_info[u'top'], bound_info[u'right'], bound_info[
                    u'bottom']
                return (left, top, right, bottom)

        elif device.device_type() == DeviceType.DEVICE_IOS:
            session = device.wda_session()
            if session is None:
                logger.error("wait_element_by_text failed : session is not set")
                return None
            elem = AutomationHelperNative.__get_ios_elem_by_text(device, text)
            if elem:
                rect = elem.bound
                return (rect.x, rect.y, rect.x + rect.width, rect.y + rect.height)

        return None
