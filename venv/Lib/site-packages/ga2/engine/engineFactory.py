from ga2.engine.engine import *
from ga2.engine.unityEngine import *
from ga2.engine.UE4Engine import *

class EngineFactory:
    __engineTypeMap = {"Unity3D": UnityEngine, "UE4": UE4Engine}

    # engine_type  is s string contained in the result of get_sdk_version, to indicate the enginetype
    @staticmethod
    def register_new_engine_type(connector_type):
        EngineFactory.__engineTypeMap[connector_type.engine_type()] = connector_type

    @staticmethod
    def recognize_engine_type(version_info):
        for key in EngineFactory.__engineTypeMap:
            if version_info.engine == key:
                return key
        return None

    @staticmethod
    def create_engine_connector(engine_type, address, port):
        if engine_type not in EngineFactory.__engineTypeMap.keys():
            return None
        return EngineFactory.__engineTypeMap[engine_type](address, port)
