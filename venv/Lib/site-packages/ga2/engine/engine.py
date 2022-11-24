# -*-coding:utf-8-*-
import re
import abc, six
from ga2.common.socketClient import SocketClient
from ga2.common.wetestExceptions import *
from ga2.engine.element import Element
from ga2.engine.protocol import Commands, TouchEvent
from ga2.common.loggerConfig import logger

from enum import Enum


# class EngineType(Enum):
#     Unity=0,
#     UE4=1

class VersionInfo(object):
    """
    Attributes:
        engine_version:引擎版本信息,如5.1.0bf
        engine:Unity
        sdk_version:wetest sdk的版本信息
    """

    def __init__(self, engine_version, engine, sdk_version, ui_type):
        self.engine_version = engine_version
        self.engine = engine
        self.sdk_version = sdk_version
        self.ui_type = ui_type

    def __str__(self):
        return "Engine = {0} {1},WeTest SDK = {2},UI={3}".format(self.engine, self.engine_version, self.sdk_version,
                                                                 self.ui_type)


class ElementBound(object):
    """
    Attributes:
        Element在屏幕上显示的位置和大小，(x,y)为中心点坐标系以屏幕左上角为坐标原点
        __________ x
        |
        |
        |
        y
        x:element与屏幕左侧的距离
        y:element与屏幕上边的距离
        width:element的宽
        height:element的高
        visible:是否可视化，在3D物体中
    """

    def __init__(self, x, y, width, height, visible=True):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = visible

    def __str__(self):
        return "  point = ({0},{1}) width = {2}  height = {3},visible={4}".format(self.x, self.y, self.width,
                                                                                  self.height, self.visible)

    def __repr__(self):
        return self.__str__()

    def __nonzero__(self):
        return self.visible


class WorldBound(object):
    """
        represents an axis aligned bounding box.
    """

    def __init__(self, _id, _existed):
        self.id = _id
        self.existed = _existed

        # center_x,center_y,center_z,the center of the bounding box
        self.center_x = 0
        self.center_y = 0
        self.center_z = 0

        # the extents of the box,
        self.extents_x = 0
        self.extents_y = 0
        self.extents_z = 0

    def __str__(self):
        return "center = ({0},{1},{2}) extents = ({3},{4},{5})".format(self.center_x, self.center_y, self.center_z,
                                                                       self.extents_x, self.extents_y, self.extents_z)


@six.add_metaclass(abc.ABCMeta)
class GameEngine(object):
    """
        Only support Unity engine at this time
    """

    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.sdk_version = None
        self.socket = SocketClient(self.address, self.port)

    def engine_type(self):
        pass

    def get_sdk_version(self):
        """ 获取引擎集成的SDK的版本信息

        获取SDK的版本信息，GameSDKVersionInfo
        :return:
            返回的信息包括引擎版本，引擎和SDK版本信息,class:VersionInfo
            example:
                {‘engine_version’：‘5.1.0bf’，
                ‘engine’：‘Unity’,
                'sdk_version':10}
        :rtype: VersionInfo
        :raise:
            WeTestRuntimeError
        """
        ret = self.socket.send_command(Commands.GET_VERSION)
        engine = ret.get("engine", None)
        sdk_version = ret.get("sdkVersion", None)
        engine_version = ret.get("engineVersion", None)
        ui_type = ret.get("sdkUIType", None)
        version = VersionInfo(engine_version, engine, sdk_version, ui_type)
        return version

    def jump_building(self, name):
        """
            通过jump_building跳转到对应building
        :param name:
            jump_building的参数
        :Usage:
            >>>import wpyscripts.manager as manager
            >>>engine=manager.get_engine()
            >>>button=engine.jump_building()
        :return:
            status:0
        :rtype: Element
        :raise:
        """
        ret = self.socket.send_command(Commands.JUMP_BUILDING, name)
        if ret:
            return 0
        else:
            return None

    #
    # def input_text_set(self, element, text):
    #     """
    #             设置坐标
    #             :param :element,text
    #
    #             :Usage:
    #                 >>>import wpyscripts.manager as manager
    #                 >>>engine=manager.get_engine()
    #                 >>>text=engine.input_text_set(element,text)
    #             :return:成功与否
    #             """
    #     ret = self.socket.send_command(Commands.SET_INPUT_TEXT_VC, {"element": element, "text": text})
    #     if ret:
    #         return ret
    #     else:
    #         return None

    def find_element(self, name):
        """
            通过GameObject.Find查找对应的GameObject
        :param name:
            GameObject.Find的参数
        :Usage:
            >>>engine=GameEngine("127.0.0.1",12345)
            >>>button=engine.find_element('/Canvas/Panel/Button')
        :return:
            a instance of Element if find the GameObject,else return  None
            example:
            {"object_name":"/Canvas/Panel/Button",
            "instance":4257741}
        :rtype: Element
        :raise:
        """
        ret = self.socket.send_command(Commands.FIND_ELEMENTS, [name])
        if ret:
            ret = ret[0]
            if ret["instance"] == -1:
                return None
            else:
                return Element(ret["name"], ret["instance"])
        else:
            return None

    @abc.abstractmethod
    def find_elements_path(self, path):
        pass

    @abc.abstractmethod
    def get_element_text(self, element):
        pass

    @abc.abstractmethod
    def get_element_bound(self, element):
        pass

    def _get_dump_tree(self):
        """
        获取dump tree
        :return: xml string
        """
        ret = self.socket.send_command(Commands.DUMP_TREE)
        return ret

    def get_scene(self):
        """
            获取当前界面的scene名称
        :Usage:
            >>>import wpyscripts.manager as manager
            >>>engine=manager.get_engine()
            >>>current_scene=engine.get_scene()
        :return:当前scene的名称
        :raise: WeTestRuntimeError
        """
        ret = self.socket.send_command(Commands.GET_CURRENT_SCENE)
        return ret





