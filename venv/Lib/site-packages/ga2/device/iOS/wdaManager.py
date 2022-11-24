# -*- coding: UTF-8 -*-

import logging
from ga2.device.iOS import wda

logger = logging.getLogger(__name__)


class WdaManager(object):
    session_map = {}

    def __init__(self, wdaport, wdahost="127.0.0.1"):
        self.__wdaport = wdaport
        self.wda_client = wda.Client('http://%s:%s' % (wdahost, str(self.__wdaport)))
        self._cur_wda_session = None  # self.wda_client.session(None)

    def get_port(self):
        return self.__wdaport

    def new_session(self, bundleid=None):
        self._cur_wda_session = self.wda_client.session(bundleid)
        self.session_map[bundleid] = self._cur_wda_session
        return self._cur_wda_session

    def get_session(self, bundleid=None):
        if bundleid is None:
            if self._cur_wda_session is None:
                self._cur_wda_session = self.new_session(None)
            return self._cur_wda_session
        elif bundleid in self.session_map.keys():
            return self.session_map[bundleid]
        else:
            logger.error("bundleid:" + bundleid + "s not in session map")
            return None

    def get_top_bundleid(self):
        session = self.wda_client.session()
        bundleid = session.bundle_id
        return bundleid

    def close_session(self, bundleid):
        if bundleid is None:
            self._cur_wda_session.close()
            self._cur_wda_session = None
            self.new_session(None)
            for key, value in list(self.session_map.items()):
                if value == self._cur_wda_session:
                    self.session_map.pop(key)
        elif bundleid in self.session_map.keys():
            session = self.session_map.pop(bundleid)
            if self._cur_wda_session == session:
                self._cur_wda_session = None
            session.close()
        else:
            logger.error("bundleid:" + bundleid + "s not in session map")

#
# class WdaManager(object):
#
#     __instance=None
#     sessionMap={}
#     def __init__(self,wdaport):
#         self.__wdaport = os.environ.get("WDA_LOCAL_PORT", wdaport)
#         self.wda_client = wda.Client('http://localhost:%s' % str(self.__wdaport))
#         self._cur_wda_session=self.wda_client.session(None)
#
#     def get_port(self):
#         return self.__wdaport
#
#     def new_session(self,bundleid):
#         self._cur_wda_session = self.wda_client.session(bundleid)
#         self.sessionMap[bundleid]=self._cur_wda_session
#         return self._cur_wda_session
#
#     def get_session(self,bundleid=None):
#         if bundleid is None:
#             if self._cur_wda_session is None:
#                 self._cur_wda_session = self.new_session(None)
#             return self._cur_wda_session
#         elif bundleid in self.sessionMap.keys():
#             return self.sessionMap[bundleid]
#         else:
#             logger.error("bundleid:"+bundleid + "s not in session map")
#             return None
#
#
#
#     def close_session(self,bundleid=None):
#         if bundleid is None:
#             self._cur_wda_session.close()
#             self._cur_wda_session = None
#             self.new_session(None)
#             for key,value in self.sessionMap.items():
#                 if value == self._cur_wda_session:
#                     self.sessionMap.pop(key)
#         elif bundleid in self.sessionMap.keys():
#             session=self.sessionMap.pop(bundleid)
#             session.close()
#         else:
#             logger.error("bundleid:" + bundleid + "s not in session map")
#
