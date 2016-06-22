import flask_restful
from bson.objectid import ObjectId
from common import parse_json
from common import response_json
from database import mongodb
from flask import Blueprint
from flask import jsonify
from flask import request
from cicle_manager.simple_life_cicle_manager import SimpleLifeCicleManagerImpl

api_v1_bp = Blueprint('api_v1', __name__)
api_v1 = flask_restful.Api(api_v1_bp)

slcm = SimpleLifeCicleManagerImpl()

'''
EXAMPLE JSON
{
    "_id" : "57599969ec7a4c184fcdf33e",
    "service_description_id" : "57599969ec7a4c184fcdf33e"
    "user" : "name2"
}
'''


class ServiceInstances(flask_restful.Resource):
    def get(self):

        result = mongodb.db[mongodb.collection_si].find({"activated": True},
                                                        {"activated": 0})

        return jsonify(parse_json.decoder_list(list(result)))

    def post(self):
        data = dict(request.json)
        result = mongodb.db[mongodb.collection_si].insert(parse_json.add_validated(data))
        if result is not None:
            return jsonify(str(result))
        else:
            return response_json.action_error(request.json)


class ServiceInstanceId(flask_restful.Resource):
    def get(self, service_instance_id):
        result = mongodb.db[mongodb.collection_si].find_one(dict(_id=ObjectId(service_instance_id)))
        if result is None:
            return response_json.not_found(service_instance_id)
        return jsonify(parse_json.decoder_item(result))

    def put(self, service_instance_id):
        data = dict(request.json)
        if data['_id'] != service_instance_id:
            return response_json.action_error(service_instance_id)
        result = mongodb.db[mongodb.collection_si].update_one({"_id": ObjectId(service_instance_id)},
                                                              {"$set": parse_json.encode_item(data)
                                                               },
                                                              upsert=False)

        if result.matched_count == 1:
            return response_json.is_ok_no_content()
        else:
            return response_json.action_error(data['_id'])

    def delete(self, service_instance_id):
        result = mongodb.db[mongodb.collection_si].update_one(dict(_id=ObjectId(service_instance_id)),
                                                              {"$set": {
                                                                  "activated": False
                                                              }
                                                              })

        if result.matched_count == 1:
            return response_json.is_ok_no_content()
        else:
            return response_json.action_error(service_instance_id)


class ServiceProjectId(flask_restful.Resource):
    def get(self, service_project_id):
        return slcm.getCurrentState(service_project_id)

    def put(self, service_project_id):
        data = dict(request.json)
        return slcm.setDesiredState(service_project_id, data['state'])


api_v1.add_resource(ServiceInstances, '/service/instance')
api_v1.add_resource(ServiceInstanceId, '/service/instance/<service_instance_id>')
api_v1.add_resource(ServiceProjectId, '/service/instance/project/<service_project_id>')