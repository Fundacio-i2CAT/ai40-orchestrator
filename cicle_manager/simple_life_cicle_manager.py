from common import paramiko_conexions
from cicle_manager.life_cicle_manager import LifeCicleManager
from common.utils import get_state
from common.paramiko_conexions import get_connect_instances


class SimpleLifeCicleManagerImpl(LifeCicleManager):
    def __init__(self, data):
        self._instance = get_connect_instances(data)
        self._data = data

    def set_desired_state(self, state):
        return connect_vm(self._data, False, get_state(state.upper()))

    def get_current_state(self):
        return connect_vm(self._data, True, '')


def connect_vm(data, is_current_state, status):
    result = None
    if data.get('context_type').lower() == 'ssh':
        context = data.get('context')
        if is_current_state:
            command = "sudo systemctl is-active " + context.get('service_name')
        else:
            command = "sudo systemctl " + status + " " + context.get('service_name')
        result = paramiko_conexions.connect_by_ssh(context, command, is_current_state)
    return result
