from common.flask_app import app
from common import config_parser
from database import mongodb
from flask import jsonify
from common import parse_json
from common import status_code
from flask import request
from bson.objectid import ObjectId


@app.route("/service/instance", methods=["GET"])
def get_all_service():
    result = mongodb.db[mongodb.collection_si].find({})
    return jsonify(parse_json.decoder_list(list(result)))


@app.route("/service/instance", methods=["POST"])
def create():
    data = dict(request.json)

    result = mongodb.db[mongodb.collection_si].insert(dict(service_description={
        "$id": ObjectId(data['service_description_id']),
        "$ref": mongodb.collection_sd
    }), check_keys=False)
    if result is not None:
        return jsonify(str(result))
    else:
        return status_code.action_error(request.json)


if __name__ == "__main__":
    app.run(
        host=config_parser.config.get("flask", "url"),
        port=int(config_parser.config.get("flask", "port"))
    )
