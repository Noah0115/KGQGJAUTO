
from ga2.common.cmdExecuter import CmdExecuter


class IMobileDevice():

    def __init__(self, udid):
        self.udid = udid

    def install(self, ipapath):
        cmd = "ideviceinstaller -i " + ipapath
        if self.udid != None:
            cmd = " -u " + self.udid
        CmdExecuter.execute_and_wait(cmd)

    @staticmethod
    def get_device_list():
        cmd = "idevice_id -l "
        return CmdExecuter.execute_and_wait(cmd)

    def uninstall(self, bundleid):
        cmd = "ideviceinstaller -U " + bundleid
        if self.udid != None:
            cmd = " -u " + self.udid
        CmdExecuter.execute_and_wait(cmd)
