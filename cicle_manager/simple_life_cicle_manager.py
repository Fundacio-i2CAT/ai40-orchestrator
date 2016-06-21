from common import paramiko_conexions
from common.config_parser import URL_CATALOG_CONTEXT
from cicle_manager.life_cicle_manager import LifeCicleManager
import requests
import json
import ast
from common.utils import get_state

class SimpleLifeCicleManagerImpl(LifeCicleManager):
    def setDesiredState(self, service_project_id, state):
        data = get_context(service_project_id)
        return connect_vm(data, False, get_state(state.upper()))

    def getCurrentState(self, service_project_id):
        data = get_context(service_project_id)
        return connect_vm(data, True, '')


def get_context(service_project_id):
    # Connect to BBDD . Get Context
    result = requests.get(URL_CATALOG_CONTEXT + service_project_id)
    data = json.loads(result.text)
    return data


def connect_vm(data, is_current_state, status):
    result = None
    if data.get('context_type').lower() == 'ssh':
        context = ast.literal_eval(data.get('context'))
        if is_current_state:
            command = "sudo systemctl is-active " + context.get('service_name')
        else:
            command = "sudo systemctl " + status + " " + context.get('service_name')
        result = paramiko_conexions.connect_by_ssh(context, command, is_current_state)
    return result