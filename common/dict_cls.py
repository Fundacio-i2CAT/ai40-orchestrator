from cicle_manager.openstack_life_cicle_manager import OpenstackLifeCicleManagerImpl
from cicle_manager.simple_life_cicle_manager import SimpleLifeCicleManagerImpl
from enums.final_state import FinalState
from enums.openstack_enum import OpenstackEnum

cls_dict = {
    "ssh": SimpleLifeCicleManagerImpl,
    "openstack": OpenstackLifeCicleManagerImpl
}

enum_dict = {
    "ssh": FinalState.INACTIVE.value,
    "openstack": OpenstackEnum.DESTROYED.value
}


def get_cls(context_type):
    return cls_dict[context_type]


def get_state_enum_value(context_type):
    return enum_dict[context_type]
