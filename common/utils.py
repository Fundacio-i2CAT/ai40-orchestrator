from bson import ObjectId
from common import parse_json
from database import mongodb
from enums.desired_state import DesiredState
from enums.final_state import FinalState
from enums.openstack_enum import OpenstackEnum
from common.config_parser import URL_CATALOG_CONTEXT
import requests
import json


def get_state_slcm(state):
    switcher = {
        "ACTIVE": FinalState.ACTIVE.value,
        "INACTIVE": FinalState.INACTIVE.value,
        "RUNNING": DesiredState.RUNNING.value,
        "DEPLOYED": DesiredState.DEPLOYED.value,
        "PROVISIONED": get_command_provisioned(state),
    }
    return switcher.get(state)


def get_state_olcm(state):
    switcher = {
        "ACTIVE": OpenstackEnum.ACTIVE.value,
        "INACTIVE": OpenstackEnum.SHUTOFF.value,
        "RUNNING": OpenstackEnum.RUNNING.value,
        "DEPLOYED": OpenstackEnum.DEPLOYED.value,
        "DESTROYED": OpenstackEnum.DESTROYED.value,
        "SHUTOFF": OpenstackEnum.SHUTOFF.value,
    }
    return switcher.get(state)


def get_command_provisioned(final_state):
    if final_state == "RUNNING":
        return "start"
    else:
        return "stop"


def get_context(service_project_id):
    # Connect to BBDD . Get Context
    result = requests.get(URL_CATALOG_CONTEXT + service_project_id)
    data = json.loads(result.text)
    return data


def add_validated_status(item):
    if 'activated' not in item:
        item['activated'] = True
    if 'status' not in item:
        item['status'] = 'PROVISIONED'
    return item


def find_one(service_instance_id):
    return mongodb.db[mongodb.collection_si].find_one(dict(_id=ObjectId(service_instance_id)))


def update_one(service_instance_id, data):
    return mongodb.db[mongodb.collection_si].update_one({"_id": ObjectId(service_instance_id)},
                                                        {"$set": parse_json.encode_item(data)
                                                         },
                                                        upsert=False)
