from common.flask_app import app
from common import config_parser
from database import mongodb
from flask import jsonify
from common import parse_json
from common import status_code
from flask import request
from bson.objectid import ObjectId
from bson.dbref import DBRef


@app.route("/service/instance", methods=["GET"])
def get_all_service():
    result = mongodb.db[mongodb.collection_si].find({"activated": True},
                                                    {"activated": 0})
    return jsonify(parse_json.decoder_list(list(result)))


@app.route("/service/instance/<service_instance_id>", methods=["GET"])
def get_service(service_instance_id):
    result = mongodb.db[mongodb.collection_si].find_one(dict(_id=ObjectId(service_instance_id)))
    if result is None:
        return status_code.not_found(service_instance_id)
    return jsonify(parse_json.decoder_item(result))


'''
EXAMPLE JSON
{
    "service_description_id" : "57599969ec7a4c184fcdf33e"
}
'''


@app.route("/service/instance", methods=["POST"])
def create():
    data = dict(request.json)
    result = mongodb.db[mongodb.collection_si].insert({"service_description":
                                                                    DBRef(mongodb.collection_sd,
                                                                          ObjectId(data['service_description_id']))
                                                       })
    if result is not None:
        return jsonify(str(result))
    else:
        return status_code.action_error(request.json)


'''
EXAMPLE JSON
{
    "_id" : "57599969ec7a4c184fcdf33e",
    "service_description_id" : "57599969ec7a4c184fcdf33e"
}
'''


@app.route("/service/instance/<service_instance_id>", methods=["PUT"])
def update(service_instance_id):
    data = dict(request.json)
    if data['_id'] != service_instance_id:
        return status_code.action_error(service_instance_id)
    result = mongodb.db[mongodb.collection_si].update_one({"_id": ObjectId(service_instance_id)},
                                                          {"$set": {"service_description":
                                                                        DBRef(mongodb.collection_sd,
                                                                              ObjectId(data['service_description_id']))
                                                                    }
                                                           },
                                                          upsert=False)

    if result.matched_count == 1:
        return status_code.is_ok_no_content()
    else:
        return status_code.action_error(data['_id'])


@app.route("/service/instance/<service_instance_id>", methods=["DELETE"])
def delete(service_instance_id):
    result = mongodb.db[mongodb.collection_si].update_one(dict(_id=ObjectId(service_instance_id)),
                                                          {"$set": {
                                                                    "activated": False
                                                                }
                                                           })
    if result.matched_count == 1:
        return status_code.is_ok_no_content()
    else:
        return status_code.action_error(service_instance_id)

if __name__ == "__main__":
    app.run(
        host=config_parser.config.get("flask", "url"),
        port=int(config_parser.config.get("flask", "port"))
    )
