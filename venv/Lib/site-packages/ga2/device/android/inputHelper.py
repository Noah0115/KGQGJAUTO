# -*- coding: UTF-8 -*-

from ga2.common import imapUtf7
from ga2.device.android.adbProcess import *
import platform


class InputHeler:

    @staticmethod
    def input_char(c, serial):
        if c != " ":
            cmd = 'shell input text ' + c
            adb_wait(cmd, serial)
        else:
            cmd = 'shell input keyevent 62'
            adb_wait(cmd, serial)
        time.sleep(1)

    '''
        input string without space
    '''

    @staticmethod
    def input_word(word, serial):
        if isinstance(word, str):
            word = imapUtf7.encode(word.decode("utf-8"))
        else:
            word = imapUtf7.encode(word)

        cmd = 'shell input text ' + '\\\"' + word + '\\\"'
        if platform.system() == "Linux":
            cmd = 'shell ' + '\"' + 'input text ' + '\\\"' + word + '\\\"' + '\"'
        adb_wait(cmd, serial)

    @staticmethod
    def ime_action(ime_action_code, serial):
        cmd = "shell am broadcast -a ADB_EDITOR_CODE --ei code " + str(ime_action_code)
        adb_wait(cmd, serial)
        time.sleep(1)

    @staticmethod
    def input_text(text, need_one_by_one, serial):
        if need_one_by_one:
            for c in text:
                InputHeler.input_char(c, serial)
        else:
            cur_seg = ""
            for c in text:
                if c == ' ':  # some android device will not handle space in input
                    if len(cur_seg) > 0:
                        InputHeler.input_word(cur_seg, serial)
                        cur_seg = ""
                        time.sleep(1)
                    InputHeler.input_char(c, serial)
                else:
                    cur_seg += c
            if len(cur_seg) > 0:
                InputHeler.input_word(cur_seg, serial)
                time.sleep(1)


import sys

if __name__ == '__main__':
    if (len(sys.argv) < 2):
        print("error ... please input the chinese word you want to type in")
        exit(-1)
    InputHeler.input_text(sys.argv[1], False, "012345678F")
