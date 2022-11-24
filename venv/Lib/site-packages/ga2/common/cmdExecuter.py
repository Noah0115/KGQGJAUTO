import sys
from ga2.common.loggerConfig import *
import subprocess
import threading

class CmdExecuter:

    '''
    execute a command by shell and return its output
    '''
    @staticmethod
    def execute_and_wait(cmdline):
        logger.info("executeAndWait: "+cmdline)
        if 'posix' in sys.builtin_module_names:
            process = subprocess.Popen(cmdline,shell=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT, preexec_fn=os.setsid)
        else:
            process = subprocess.Popen(cmdline, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retlines=[]
        while True:
            line = process.stdout.readline()
            if not line :
                break
            logger.debug(line.strip())
            retlines.append(line.strip())

        return retlines

    '''
    execute a command by shell and return the thread instance
    '''
    @staticmethod
    def execute_no_wait(cmdline):
        t = threading.Thread(target=CmdExecuter.execute_and_wait, args=(cmdline,))
        t.setDaemon(True)
        t.start()
        logger.info("execute_no_wait end")
        return t



