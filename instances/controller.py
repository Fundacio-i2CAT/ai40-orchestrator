import flask_restful
from common import parse_json
from common import response_json
from common.dict_cls import get_cls
from common.dict_cls import get_state_enum_value
from common.utils import add_validated_status
from common.utils import find_one
from common.utils import get_state_slcm
from common.utils import update_one
from database import mongodb
from enums.final_state import FinalState
from flask import Blueprint
from flask import jsonify
from flask import request

api_v1_bp = Blueprint('api_v1', __name__)
api_v1 = flask_restful.Api(api_v1_bp)

dict_instances = {}


class ServiceInstances(flask_restful.Resource):
    def get(self):
        result = mongodb.db[mongodb.collection_si].find({"activated": True},
                                                        {"activated": 0})

        return jsonify(parse_json.decoder_list(list(result)))

    def post(self):
        data = dict(request.json)
        lcm = get_cicle_manager_type(data)
        instance = lcm.get_instance()
        if instance is not None:
            data = parse_json.encode_item(data)
            if hasattr(instance, 'id'):
                result = mongodb.db[mongodb.collection_si].insert_one(add_validated_status(data, instance.id))
            else:
                result = mongodb.db[mongodb.collection_si].insert_one(add_validated_status(data, ''))
            if result.inserted_id is not None:
                dict_instances.update({str(result.inserted_id): lcm})
                return jsonify({"service_instance_id": str(result.inserted_id)})
            else:
                return response_json.action_error(request.json)
        else:
            context = data.get('context')
            message_json = "It isn't possible to connect. Hostname = " + \
                           context.get('host') + " Port = " + str(context.get('port'))
            return response_json.connect_vm_error(message_json)


class ServiceInstanceId(flask_restful.Resource):
    def get(self, service_instance_id):
        data = find_one(service_instance_id)
        if data is None or not data['activated']:
            return response_json.not_found('Not found ' + service_instance_id)
        lcm = get_cls_in_dict(data)
        put_cls_in_dict(service_instance_id, lcm)
        return get_current_status_and_update(lcm, service_instance_id)

    def put(self, service_instance_id):
        data = dict(request.json)
        if data['_id'] != service_instance_id:
            return response_json.action_error(service_instance_id)
        result = update_one(service_instance_id, data)

        if result.matched_count == 1:
            return response_json.is_ok_no_content()
        else:
            return response_json.action_error(data['_id'])

    def delete(self, service_instance_id):
        data = find_one(service_instance_id)
        if data is None:
            return response_json.not_found('Not found ' + service_instance_id)
        data = parse_json.decoder_item(data)
        state_enum = get_state_enum_value(data['context_type'].lower())
        lcm = get_cls_in_dict(data)
        code = lcm.set_desired_state(state_enum)
        if code is None:
            context = data.get('context')
            message_json = "It isn't possible to connect. Hostname = " + \
                           context.get('host') + " Port = " + str(context.get('port'))
            return response_json.not_found(message_json)
        # Actualizamos en base de datos
        data_state = {"status": state_enum, "activated": False}
        result = update_one(service_instance_id, data_state)
        if result.matched_count == 1:
            put_cls_in_dict(service_instance_id, lcm)
            return response_json.is_ok_no_content()
        else:
            return response_json.action_error(service_instance_id)


class ServiceProjectId(flask_restful.Resource):
    def get(self, service_instance_id):
        data = find_one(service_instance_id)
        if data is None or not data['activated']:
            return response_json.not_found('Not found ' + service_instance_id)
        lcm = get_cls_in_dict(data)
        put_cls_in_dict(service_instance_id, lcm)
        return get_current_status_and_update(lcm, service_instance_id)

    def put(self, service_instance_id):
        state = dict(request.json)
        # Si nos piden a un estado PROVISIONED --> ERROR
        if state['state'].upper() == FinalState.PROVISIONED.value:
            return response_json.action_error(service_instance_id)
        if get_state_slcm(state['state'].upper()) is None:
            return response_json.not_found('Not found ' + service_instance_id + ' and state = ' + state['state'])
        data = find_one(service_instance_id)
        if data is None:
            return response_json.not_found('Not found ' + service_instance_id)
        # Miramos el estado actual
        if data.get('status').upper() == state['state'].upper():
            result = {'state': state['state']}
            return result
        lcm = get_cls_in_dict(data)
        code = lcm.set_desired_state(state['state'])
        if code is None:
            return response_json.action_error('This instance was already in state ' + state['state'])
        # Actualizamos en base de datos
        data_state = {"status": state['state'].lower()}
        result = update_one(service_instance_id, data_state)
        if result.matched_count != 1:
            return response_json.action_error(service_instance_id)
        put_cls_in_dict(service_instance_id, lcm)
        return code


api_v1.add_resource(ServiceInstances, '/service/instance')
api_v1.add_resource(ServiceInstanceId, '/service/instance/<service_instance_id>')
api_v1.add_resource(ServiceProjectId, '/service/instance/<service_instance_id>/state')


def get_cicle_manager_type(data):
    cls = get_cls(data['context_type'].lower())
    return cls(data)


def get_cls_in_dict(data):
    if str(data['_id']) in dict_instances.keys():
        return dict_instances[str(data['_id'])]
    else:
        return get_cicle_manager_type(data)


def put_cls_in_dict(service_instance_id, lcm):
    if service_instance_id not in dict_instances.keys():
        dict_instances.update({service_instance_id: lcm})

def get_current_status_and_update(lcm, service_instance_id):
    result = lcm.get_current_state()
    if 'status' in result:
        result_update = update_one(service_instance_id, {"status": result['status']})
        if result_update.matched_count != 1:
            return response_json.action_error(service_instance_id)
    return result
