#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Chunk repo server"""

import flask_restful
from flask import Flask, Blueprint, request, send_from_directory
from flask_restful import Api, abort
from flask_cors import CORS, cross_origin

URL_PREFIX = ''
HOST = '0.0.0.0'
PORT = 6062
APP = Flask(__name__, static_folder='static')
cors = CORS(APP, resources={r"/upload": {"origins": "*"}})
API_V2_BP = Blueprint('api_v1', __name__)
API_V2 = Api(API_V2_BP)

class Main(flask_restful.Resource):
    
    def get(self,path):
        return send_from_directory('static', path)

class Upload(flask_restful.Resource):

    def post(self):
        print "#############################################"
        if 'file' in request.files:
            my_file = request.files['file']
            print my_file.filename
            my_file.save('chunks/{0}'.format(my_file.filename))
        else:
            print request.get_json()
        return 200

API_V2.add_resource(Upload,'/upload')
API_V2.add_resource(Main,'/<path>')

if __name__ == "__main__":
    print "Chunk repo server"
    APP = Flask(__name__)
    APP.register_blueprint(
        API_V2_BP,
        url_prefix=URL_PREFIX
    )
    APP.run(debug=False, host=HOST, port=PORT)
