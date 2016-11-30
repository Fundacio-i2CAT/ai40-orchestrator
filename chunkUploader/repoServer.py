#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Chunk repo server"""

import flask_restful
from flask import Flask, Blueprint, request, send_from_directory
from flask_restful import Api, abort
from flask_cors import CORS, cross_origin
import os

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

class Chunked(flask_restful.Resource):

    def post(self):
        print "#############################################"
        if 'file' in request.files:
            my_file = request.files['file']
            print my_file.filename
            my_file.save('chunks/{0}'.format(my_file.filename))
        else:
            print request.get_json()
        return 200

class Upload(flask_restful.Resource):

    def post(self):
        data = request.get_json()
        os.system("cat chunks/{0}* > {1}".format(data['uuid'],data['filename']))
        os.system("rm -rf chunks/*")
        os.system("md5sum {0} > md5.txt".format(data['filename']))
        md5 = None
        with open("md5.txt") as fh:
            md5 = fh.read()
        print md5
        print data['md5sum']
        return 200


API_V2.add_resource(Chunked,'/chunked')
API_V2.add_resource(Upload,'/upload')
API_V2.add_resource(Main,'/<path>')

if __name__ == "__main__":
    print "Chunk repo server"
    APP = Flask(__name__)
    APP.register_blueprint(
        API_V2_BP,
        url_prefix=URL_PREFIX
    )
    APP.run(debug=True, host=HOST, port=PORT)
