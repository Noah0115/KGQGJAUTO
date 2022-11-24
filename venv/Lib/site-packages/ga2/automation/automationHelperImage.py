from ga2.common.loggerConfig import logger
from ga2.common.utils import callLog
from ga2.device.deviceOrientation import DeviceOrientation
from ga2.common.utils import *
from ga2.cloud.reporter import Reporter
from ga2.common.WebDriverWait import WebDriverWait
from ga2.uiimage.tmplatematcher import TemplateMatcher
# from ga2.uiimage.featurematcher import FeatureMatcher

import cv2


class AutomationHelperImage:

    @staticmethod
    def rescale(rect, width_src, height_src, width_target, height_target):
        ret = list(rect)
        if (height_src - width_src) * (height_target - width_target) < 0:
            ret[0] = rect[0] * 1.0 / width_src
            ret[2] = rect[2] * 1.0 / width_src
            ret[1] = rect[1] * 1.0 / height_src
            ret[3] = rect[3] * 1.0 / height_src
        else:
            ret[0] = rect[0] * 1.0 / width_src
            ret[2] = rect[2] * 1.0 / width_src
            ret[1] = rect[1] * 1.0 / height_src
            ret[3] = rect[3] * 1.0 / height_src
        return ret

    @staticmethod
    def rotate(rect, target_orientation):
        ret = list(rect)
        if target_orientation == DeviceOrientation.PORTRAIT:
            return ret
        elif target_orientation == DeviceOrientation.LANSCAPE:
            ret[0] = rect[1]
            ret[1] = 1.0 - rect[0]
            ret[2] = rect[3]
            ret[3] = 1.0 - rect[2]
        elif target_orientation == DeviceOrientation.PORTRAIT_UPSIDEDOWN:
            ret[0] = 1.0 - rect[0]
            ret[1] = 1.0 - rect[1]
            ret[2] = 1.0 - rect[2]
            ret[3] = 1.0 - rect[3]
        elif target_orientation == DeviceOrientation.LANDSCAPERIGHT:
            ret[0] = 1.0 - rect[1]
            ret[1] = rect[0]
            ret[2] = 1.0 - rect[3]
            ret[3] = rect[2]
        return ret

    @staticmethod
    def trans_rect_to_device(screenimg, rect, device, portrait):
        display_size = device.display_size()
        logger.debug("trans_rect_to_device : display_size {}x{}".format(display_size[0],display_size[1]))
        ret = AutomationHelperImage.rescale(rect, screenimg.shape[1], screenimg.shape[0], display_size[0],
                                            display_size[1])
        logger.debug("scaled result : {}".format(ret))
        if portrait:  #the screenimg has been portraited
            ret = AutomationHelperImage.rotate(ret,  device.orientation())

        return ret

    @staticmethod
    def get_result_by_template(device, param):
        template_path = param["path"]
        portrait = param["portrait"] if "portrait" in param else True
        height = param["height"] if "height" in param else None

        # featureMatcher = FeatureMatcher()
        try:
            screenimg = device.screenshot(portrait=portrait, height=height)
            if screenimg is None:
                return None
            template = cv2.imread(template_path, cv2.IMREAD_COLOR)
            if template is None:
                return None
            if screenimg.shape[2] != template.shape[2]:  # remove alpha value
                screenimg = screenimg[:, :, :3]
            print(screenimg.shape[1], screenimg.shape[0])
            result = TemplateMatcher().searchImage(templateImage=template, sceneImage=screenimg)
            if result and result.rect:
                rect = AutomationHelperImage.trans_rect_to_device(screenimg, result.rect, device, portrait)
                logger.debug("template match result : {} trans to {} ".format(result.rect, rect))
                return rect

            return result.rect if result and result.rect else None
        except Exception as e:
            logger.exception(e)
            return None

        # print(result)

    @staticmethod
    def wait_element_by_image_template(device, param, timeout):
        if device:
            bound = None
            try:
                bound = WebDriverWait(timeout, 2).until(AutomationHelperImage.get_result_by_template, device, param)
                print(bound)  # (sx,sy,dx,dy)
            except Exception as e:
                logger.warn("element wait timeout:" + str(param))
            return bound
        return None

    @staticmethod
    def handle_element_by_image_template(device, param, operator, **kwargs):
        if device:
            rect = AutomationHelperImage.get_result_by_template(device, param)
            if rect is None:
                logger.error("image element is not found : " + str(param))
                return None
            target_pos = ((rect[0] + rect[2]) / 2, (rect[1] + rect[3]) / 2)
            if is_cloud_mode():
                (width, height) = device.display_size()
                Reporter().screenshot_with_mark(width, height, target_pos[0], target_pos[1])
            operator(target_pos[0], target_pos[1], **kwargs)
            return rect
        return None


