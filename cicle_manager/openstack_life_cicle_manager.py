from cicle_manager.life_cicle_manager import LifeCicleManager
from common.openstack_common import create_connection
from common.openstack_common import create_instance
from common.openstack_common import get_instance
from common.utils import get_state_olcm
from enums.openstack_enum import OpenstackEnum
from common.response_json import not_found
from common.utils import get_state_olcm


class OpenstackLifeCicleManagerImpl(LifeCicleManager):
    def __init__(self, data):
        self._conn = create_connection(data['context']['openstack'])
        if 'openstack_id' not in data['context']['openstack']:
            self._instance = create_instance(self._conn, data['context']['openstack'])
        else:
            self._instance = get_instance(self._conn, data['context']['openstack']['openstack_id'])
        self._data = data

    def set_desired_state(self, state):
        if state == OpenstackEnum.DESTROYED.value:
            try:
                self._instance.delete(self._conn.session)
                return 1
            except Exception as e:
                return None
        else:
            dict_fs = get_state_olcm(state.upper())
            return self._instance.action(self._conn.session, dict_fs)

    def get_current_state(self):
        try:
            status = self._conn.compute.get_server(self._instance).status
            return {"status": get_state_olcm(status)}
        except Exception as e:
            return not_found('Server not found ' + str(self._data['_id']))
