# -*- coding: UTF-8 -*-
import traceback
import time
import threading
import logging
import os

logger = logging.getLogger("gautomator")


def is_cloud_mode():
    return "PLATFORM_PORT" in os.environ and os.environ.get("PLATFORM_PORT") is not None and os.environ.get("PLATFORM_PORT") != ""


isInCloudMode = is_cloud_mode


def callLog(func):
    def wrapper(*args, **kw):
        local_time = time.time()
        ret=func(*args, **kw)
        logger.debug('Call [%s] cost: %.2fs' % (func.__name__ ,time.time() - local_time))
        return ret
    return wrapper


class ErrType:
    ERR_SUCCEED = 0
    ERR_TIMEOUT = -101
    ERR_CONNECT_TO_SDK_FAILED = -102
    ERR_CONNECT_TO_UITUAOMTTOR_FAILED = -103
    ERR_LOGIN_FAILED = -104
    ERR_WDA_NOT_RUNNING = -105
    ERR_DEVICE_NOT_INITED = -106
    ERR_CLOUD_PLATFORM = -107
    ERR_INVALID_ENGINETYPE = -108
    ERR_PROCESS_NOT_FOUND = -109
    ERR_UNIMPLEMENTED = -110
    ERR_ADB = -111


