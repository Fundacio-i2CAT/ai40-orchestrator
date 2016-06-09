from common.flask_app import app
from common import config_parser
from database import mongodb
from flask import jsonify
from common import parse_json
from common import status_code
from flask import request


@app.route("/service/instance", methods=["GET"])
def get_all_service():
    result = mongodb.db[mongodb.collection_sd].find({})
    return jsonify(parse_json.decoder_list(list(result)))


@app.route("/service", methods=["POST"])
def create():
    data = dict(request.json)
    result = mongodb.db[mongodb.collection_sd].insert_one(data)
    if result.inserted_id is not None:
        return jsonify(str(result.inserted_id))
    else:
        return status_code.action_error(data['id'])


if __name__ == "__main__":
    app.run(
        host=config_parser.config.get("flask", "url"),
        port=int(config_parser.config.get("flask", "port"))
    )