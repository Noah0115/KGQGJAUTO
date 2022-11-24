
from enum import Enum


class DeviceOrientation(Enum):
    PORTRAIT = 0
    LANSCAPE = 1
    PORTRAIT_UPSIDEDOWN = 2
    LANDSCAPERIGHT = 3

WDA_ORIENTATION_MAP = {'PORTRAIT': DeviceOrientation.PORTRAIT,
                           'LANDSCAPE': DeviceOrientation.LANSCAPE,
                           'UIA_DEVICE_ORIENTATION_PORTRAIT_UPSIDEDOWN': DeviceOrientation.PORTRAIT_UPSIDEDOWN,
                           'UIA_DEVICE_ORIENTATION_LANDSCAPERIGHT': DeviceOrientation.LANDSCAPERIGHT}