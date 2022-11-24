from ga2.common.loggerConfig import logger
from ga2.common.utils import *
from ga2.cloud.reporter import Reporter
from ga2.common.WebDriverWait import WebDriverWait


class AutomationHelperEngine:

    @staticmethod
    def wait_element_by_name(device, name, timeout):
        logger.info("name : " + name + "timeout : " + str(timeout))
        if device and device.engine_connector():
            element = None
            try:
                element = WebDriverWait(timeout, 2).until(device.engine_connector().find_element, name)
                print(element)
            except Exception as e:
                logger.warn("element wait timeout: " + name + "(" + repr(e) + " )")
            return element
        return None

    @staticmethod
    def wait_element_by_path(device, path, timeout):
        if device and device.engine_connector():
            elements = None
            try:
                elements = WebDriverWait(timeout, 2).until(device.engine_connector().find_element_path, path)
                if len(elements) > 0:
                    return elements[0]
            except Exception as e:
                logger.warn("element wait timeout:" + path)
        return None

    @staticmethod
    def wait_elements_by_path(device, path, timeout):
        if device and device.engine_connector():
            elements = None
            try:
                elements = WebDriverWait(timeout, 2).until(device.engine_connector().find_elements_path, path)
                print(elements)
            except Exception as e:
                logger.warn("element wait timeout:" + path)
            return elements
        return None

    @staticmethod
    def handle_element_by_name(device, name, operator, **kwargs):
        if not device or not device.engine_connector():
            return None
        engine = device.engine_connector()
        element = engine.find_element(name)
        print(element)
        if element is None:
            logger.error("engine element is not found : " + name)
            return None
        bound = engine.get_element_bound(element)
        if bound is None:
            logger.error("engine element is not found : " + name)
            return None
        target_pos = (bound.x + bound.width / 2, bound.y + bound.height / 2)
        if is_cloud_mode():
            (width, height) = device.display_size()
            Reporter().screenshot_with_mark(width, height, target_pos[0], target_pos[1])
        operator(target_pos[0], target_pos[1], **kwargs)
        return target_pos

    @staticmethod
    def handle_element_by_self(device, element, operator, **kwargs):
        if not device or not device.engine_connector():
            return None
        engine = device.engine_connector()
        if element is None:
            logger.error("engine element is none")
            return None
        bound = engine.get_element_bound(element)
        if bound is None:
            logger.error("engine element is not found... ")
            return None
        target_pos = (bound.x + bound.width / 2, bound.y + bound.height / 2)
        if is_cloud_mode():
            (width, height) = device.display_size()
            Reporter().screenshot_with_mark(width, height, target_pos[0], target_pos[1])
        operator(target_pos[0], target_pos[1], **kwargs)
        return target_pos

    @staticmethod
    def handle_element_by_path(device, path, operator, **kwargs):
        if not device or not device.engine_connector():
            return None
        engine = device.engine_connector()
        elements = engine.find_elements_path(path)
        if elements is None or len(elements) == 0:
            logger.error("engine element is not found : " + path)
            return None
        if len(elements) > 1:
            logger.warn("multiple engine element is mathed by path : " + path)
        element = elements[0]
        bound = engine.get_element_bound(element)
        target_pos = (bound.x + bound.width / 2, bound.y + bound.height / 2)
        if is_cloud_mode():
            (width, height) = device.display_size()
            Reporter().screenshot_with_mark(width, height, target_pos[0], target_pos[1])
        operator(target_pos[0], target_pos[1], **kwargs)
        return target_pos

    @staticmethod
    def get_bound_by_name(device, name):
        if not device or not device.engine_connector():
            return None
        engine = device.engine_connector()
        element = engine.find_element(name)
        if element is None:
            logger.error("engine element is none")
            return None
        bound = engine.get_element_bound(element)
        if bound is None:
            logger.error("engine element is not found... ")
            return None
        return (bound.x, bound.y, bound.x + bound.width, bound.y + bound.height)

    @staticmethod
    def get_bound_by_path(device, path):
        if not device or not device.engine_connector():
            return None
        engine = device.engine_connector()
        elements = engine.find_elements_path(path)
        if elements is None or len(elements) == 0:
            logger.error("engine element is not found : " + path)
            return None
        if len(elements) > 1:
            logger.warn("multiple engine element is mathed by path : " + path)
        element = elements[0]
        if element is None:
            logger.error("engine element is none")
            return None
        bound = engine.get_element_bound(element)
        if bound is None:
            logger.error("engine element is not found... ")
            return None
        return (bound.x, bound.y, bound.x + bound.width, bound.y + bound.height)

    @staticmethod
    def get_bound_by_self(device, element):
        if not device or not device.engine_connector():
            return None
        engine = device.engine_connector()
        if element is None:
            logger.error("engine element is none")
            return None
        bound = engine.get_element_bound(element)
        if bound is None:
            logger.error("engine element is not found... ")
            return None

        return (bound.x, bound.y, bound.x + bound.width, bound.y + bound.height)
