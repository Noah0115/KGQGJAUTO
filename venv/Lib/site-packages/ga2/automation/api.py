from ga2.automation.automationHelper import AutomationHelper

from ga2.device.iOS.iOSDevice import *
from ga2.device.android.androidDevice import *
from ga2.automation.uiconfig import *

'''
quickly create and return a default device which will be used by other apis by default.
if multiple device is needed in a process, it's better to create device instances by user rather than using this api.
'''
def init_device(type, serial=None, gaport=None, screenshoter=None):
    if type == DeviceType.DEVICE_IOS:
        if is_cloud_mode():
            serial = os.environ.get("IOS_SERIAL", serial)
        device = IOSDevice(udid=serial, gaport=gaport, screenshoter=screenshoter)
        if device is not None:
            Device.set_default(device)
        return device
    elif type == DeviceType.DEVICE_ANDROID:
        if is_cloud_mode():
            serial = os.environ.get("ANDROID_SERIAL", serial)
        device = AndroidDevice(serial=serial, gaport=gaport,  screenshoter=screenshoter)
        if device is not None:
            Device.set_default(device)
        return device
    else:
        logger.error("device type unsupported : " + str(type))
        return None


def load_uiconfig(path):
     uiconfig = UIConfig(path)
     if uiconfig:
         UIConfig.set_default(uiconfig)
     return uiconfig


def touch_element(method, param, device=None, sleep_after=0.5):
    return AutomationHelper.touch_element(method, param, device, sleep_after)


click_element = touch_element


def wait_element(method, param, timeout=10, device=None):
    return AutomationHelper.wait_element(method, param, timeout, device)


def wait_elements(method, param, timeout=10, device=None):
    return AutomationHelper.wait_elements(method, param, timeout, device)

#
# def double_touch_element(method, param, device=None, sleep_after=0.5):
#     return AutomationHelper.double_touch_element(method, param, device , sleep_after)


def long_press_element(method, param, duration=2, device=None, sleep_after=0.5):
    return AutomationHelper.long_press_element(method, param, duration, device, sleep_after)



def get_element_bound(method, param,  device=None):
    return AutomationHelper.get_element_bound(method, param, device)