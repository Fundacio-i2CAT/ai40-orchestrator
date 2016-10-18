#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, jsonify, request, Blueprint
import flask_restful
from flask_restful import Api
from tenor_client import TenorClient
import requests 
import json

app = Flask(__name__)
api_v2_bp = Blueprint('api_v2', __name__)
api_v2 = Api(app)

tenor_client = TenorClient('http://localhost:4000')

class ServiceInstances(flask_restful.Resource):

    def get(self):
        return tenor_client.get_ns_instances()

    def post(self):
        data = request.get_json()
        context = data["context"]

        return data

#    def post(self):
        
        

class Register(flask_restful.Resource):

    def post(self):
        data = request.get_json()
        print data
        service = data['service']
        descriptor = data['descriptor']
        headers = {
            'Content-Type': 'application/json',
        }
        r = requests.post('http://localhost:4000/{0}'.format(service), 
                          headers=headers, 
                          json=descriptor)
        return r.status_code

class Nsd(flask_restful.Resource):

    def get(self):
        r = requests.get('http://localhost:4000/network-services')
        nsds = json.loads(r.text)
        ids = []
        for i in nsds:
            ids.append({"id": i['nsd']['id'],'date': i['updated_at']})
        return ids

    def post(self,ns_id=None):
        r = requests.get('http://localhost:4000/network-services')
        nsds = json.loads(r.text)
        if not ns_id:
            ns_id = nsds[-1]['nsd']['id']
        headers = {
            'Content-Type': 'application/json',
        }
        data = {
            "ns_id": ns_id,
            "callbackUrl": "http://example.com", "flavour": "basic", "pop_id": "26"
        }
        r = requests.post('http://localhost:4000/ns-instances', 
                          headers=headers, 
                          json=data)
        return r.text


api_v2.add_resource(Register,'/register')
api_v2.add_resource(Nsd, '/nsd')
api_v2.add_resource(ServiceInstances, '/service/instance')

# api_v1.add_resource(ServiceInstanceId, '/service/instance/<service_instance_id>')
# api_v1.add_resource(ServiceProjectId, '/service/instance/<service_instance_id>/state')

if __name__ == "__main__":
    print "Tablecloth (instances.controller v2 via TeNOR) ..."
    app.run(debug=True)
