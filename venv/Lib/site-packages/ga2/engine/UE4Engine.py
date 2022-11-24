# -*- coding: UTF-8 -*-
from ga2.engine.engine import *
from ga2.engine.uielement import UIElement
from ga2.common.utils import *

class UE4Engine(GameEngine):
    def __init__(self, address, port):
        super(UE4Engine, self).__init__(address, port)
        self._callback_socket = None
        self._callback_functions = {}
        self._callback_thread = None

    def engine_type(self):
        return "UE4"


    def find_elements_path(self, path):
        logger.error("find_elements_path is not implemented int UE4")
        return ErrType.ERR_UNIMPLEMENTED

    def find_elements_by_component(self, name):
        logger.error("find_elements_by_component is not implemented int UE4")
        return ErrType.ERR_UNIMPLEMENTED

    def get_element_text(self, element):
        """
            获取UMG文字内容，支持UMultiLineEditableText，UTextBlockmUMultiLineEditableTextBox及其子类UMG类型
        :param element: 查找的Element

        :Usage:
            >>>element=engine.find_element('Button')
            >>>text=engine.get_element_text(element)
        :return:文字内容
        :raises WeTestInvaildArg,WeTestRuntimeError
        """
        if element is None:
            raise WeTestInvaildArg("Invalid Instance")
        ret = self.socket.send_command(Commands.GET_ELEMENT_TEXT, element.instance)
        return ret



    def get_element_bound(self, element):
        """
        获取GameObject在屏幕上的位置和长宽高
        :param element: 查找到的GameObject

        :Usage:
            >>>
            >>>element=engine.find_element('Button')
            >>>bound=engine.get_element_bound(element)
        :return:屏幕中的位置（x,y），左上角为原点，及长宽
            examples:
            {"x":0.5，
            "y":0.5.0,
            "width":0.2
            "height":0.1}
        :rtype: ElementBound
        :raises WeTestInvaildArg,WeTestRuntimeError
        """
        if element is None:
            raise WeTestInvaildArg("Invaild Instance,element is None")

        ret = self._get_elements_bound([element])
        print(ret)
        if ret:
            result = ret[0]
            if not result["existed"]:
                return None
            else:
                return ElementBound(result["x"], result["y"], result["width"], result["height"], result["visible"])
        return None

    def _get_elements_bound(self, elements):
        send_params = [e.object_name for e in elements]
        ret = self.socket.send_command(Commands.GET_ELEMENTS_BOUND, send_params)
        return ret

