#-*- coding: UTF-8 -*-

import os
import atexit
from ga2.device.android.uiauto import uiautomator
from ga2.common.utils import *
from ga2.cloud import platformHelper
from ga2.device.android.adbProcess import *
from ga2.common.loggerConfig import logger

class UiautoManager(object):

    __device_uiauto_port=9008

    def __init__(self, serial, host, port=None ):
        self.__serial = serial

        if port is None:
            self.__local_port = os.environ.get("UIAUTOMATOR_PORT", "19008")
        else:
            self.__local_port = port
        if is_cloud_mode():
            response = platformHelper.get_platform_client().platform_forward(self.__device_uiauto_port)
            if response is None:
                return
            else:
                self.__local_port = response["localPort"]
        else:
            self.start_uiautomator_server()
        self.client = uiautomator.AutomatorDevice(serial=self.__serial, local_port=int(self.__local_port),adb_server_host=host, adb_server_port=None)


    def start_uiautomator_server(self, dialoghandler=False):
        adb_forward(self.__local_port, self.__device_uiauto_port, self.__serial)
        file_path = os.path.split(os.path.realpath(__file__))[0]
        if dialoghandler:
            jar_name = "uiautomator-stub-dialoghandler.jar"
            config_path = os.path.abspath(
                os.path.join(file_path, "..",  "libs", "wetest_dialog_config.properties"))
            #write_dialog_config(config_path)
            adb_wait("push {0} /data/local/tmp".format(config_path),self.__serial)
        else:
            jar_name="uiautomator-stub.jar"
        uiautomator_stub_path = os.path.abspath( os.path.join(file_path,"..", "libs", jar_name))
        adb_wait("push " + uiautomator_stub_path + " /data/local/tmp",self.__serial)
        uiautomator_process =adb_nowait(
            "shell uiautomator runtest " + jar_name + " -c com.github.uiautomatorstub.Stub", shell=True)
        atexit.register(adb_kill_process_by_name, "uiautomator", self.__serial)
        atexit.register(adb_remove_forward, self.__local_port, self.__serial)
        time.sleep(1)#wait for uiautomator service normal(not a good way)

    def port(self):
        return self.__local_port

    @property
    def ui_device(self):
        return self.client

    # write pkgname filter , unimplemented yet
    # def __write_dialog_config(self, config_path):
    #     if os.environ.get("PKGNAME") is None:
    #         return
    #     content = ""
    #     # with open(config_path,"r") as f:
    #     #     content=f.read()
    #
    #     textpattern = u'(^(完成|关闭|好|好的|确定|确认|安装|下次再说|暂不删除)$|(.*(?<!不|否)(忽略|允(\s)?许|同意)|继续|稍后|暂不|下一步).*)'
    #     textGroupPattern = u'((建议.*清理)|是否卸载|卸载后)&&&(取消|以后再说|下载再说);是否发送错误报告&&&否;为了给您提供丰富的图书资源&&&取消;简化备份恢复流程&&&(以后再说|下次再说)'
    #     pkgfilter = ""
    #     if os.environ.get('PKGNAME'):
    #         pkgfilter = u'(?=(^(?!' + os.environ.get("PKGNAME") + u"$)))"
    #     pkgattern = pkgfilter + u'^(?!(com.tencent.mm|com.tencent.mqq|com.tencent.mobileqq)$).*'
    #     content += "textpattern=" + textpattern + "\n"
    #     content += "textGroupPattern=" + textGroupPattern + "\n"
    #     content += "pkgattern=" + pkgattern + "\n"
    #     content += "needDialogHandler=true" + "\n"
    #
    #     with open(config_path, "w") as f:
    #         f.write(content)

    # def restart_uiautomator_server(self):


