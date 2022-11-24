# -*- coding: UTF-8 -*-

import os
import logging
import subprocess
import time
import re
logger=logging.getLogger("wetest")



def adb_wait(cmd, serial=None):
    logger.debug(cmd)
    if serial:
        command = "adb -s {0} {1}".format(serial, cmd)
    else:
        command = "adb {0}".format(cmd)
    p = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    out, err = p.communicate()
    if err is not None and len(err)>0:
        logger.error("[adb_wait] " + cmd + " error: " + str(err))
    return out, err

def adb_push(local_path, target_path,serial):
    cmd = "push {0} {1}".format(local_path, target_path )
    return adb_wait(cmd, serial)

def adb_pull(remote_path, target_path,serial):
    cmd = "pull {0} {1}".format(remote_path, target_path )
    return adb_wait(cmd, serial)

def adb_forward(pc_port, mobile_port,serial):
    cmd = "forward tcp:{0} tcp:{1}".format(pc_port, mobile_port)
    return adb_wait(cmd, serial)

def adb_remove_forward(pc_port,serial):
    cmd = "forward --remove tcp:{0} ".format(pc_port)
    return adb_wait(cmd, serial)

'''
if needStdout is true , the caller must read the process pipe out in case the subprocess hangs
'''
def adb_nowait(cmd, shell=False, serial=None, needStdout=True):
    if serial:
        command = "adb -s {0} {1}".format(serial, cmd)
    else:
        command = "adb {0}".format(cmd)
    #print "daemon: {0}".format(command)
    if needStdout is True:
        p = subprocess.Popen(command, shell=shell, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    else:
        p = subprocess.Popen(command, shell=shell)
    return p

def adb_kill_process_by_name(name, serial=None):
    pid = adb_get_pid_by_name(name,serial)
    logger.debug("[kill_process_by_name] : " + name + " pid : " + str(pid))
    if pid is not None and pid > 0:
        adb_wait("shell kill {0}".format(pid), serial)
    time.sleep(1)
    pid = adb_get_pid_by_name(name, serial)
    if pid is not None and pid > 0:
        adb_wait("shell kill -9 {0}".format(pid), serial)

def adb_get_pid_by_name(name, serial=None):
    logger.debug("[get_pid_by_name] : " + name)
    out, err = adb_wait("shell ps", serial)
    # outstr = "\n".join(out)
    pattern = "\w+\s+(\d+)\s+.+" + name
    match = re.search(pattern, out.decode("utf-8"), re.M)
    if match:
        pid = match.group(1)
        logger.debug("found process pid= {0}".format(pid))
        return int(pid)
    else:
        out, err = adb_wait("shell ps -ef", serial)
        # print(out)
        # outstr = "\n".join(out)
        match = re.search(pattern,  out.decode("utf-8"), re.M)
        if match:
            pid = match.group(1)
            logger.debug("found process pid= {0}".format(pid))
            return int(pid)
    return 0


def adb_get_top_app(serial=None):
    out, err = adb_wait("shell dumpsys window windows", serial)
    pattern = "mCurrentFocus=.*\s([^\s]*)/(.*?)}?\s"
    package = None
    match = re.search(pattern, out.decode("utf-8"), re.M)
    if match:
        package = match.group(1)
        logger.debug("found top package by adb = {0}".format(package))
    return package

def adb_get_display_size(serial=None):
    out, err = adb_wait("shell dumpsys window displays", serial)
    pattern = "cur=(\d+)x(\d+)"
    display_size = None
    match = re.search(pattern, out.decode("utf-8"), re.M)
    if match:
        display_size = (int(match.group(1)), int(match.group(2)))

    return display_size

if __name__ == "__main__":
    adb_wait("shell input tap 553 1007")
    pass
