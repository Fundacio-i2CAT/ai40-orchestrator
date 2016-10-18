#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, jsonify, request, Blueprint
import flask_restful
from flask_restful import Api
from tenor_client import TenorClient,TenorId
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
        context = data['context']['tenor']
        name = context['name']
        ns_id = tenor_client.get_last_ns_id()+1
        vnf_id = tenor_client.get_last_vnf_id()+1
        if context['vm_image_format'] == "openstack_id":
            tenor_client.create_existing_vnf(vnf_id,context['vm_image'],context['name'])
            tenor_client.create_existing_ns(ns_id,vnf_id,context['name'])
        else:
            tenor_client.create_vnf(vnf_id,context['vm_image'],context['name'])
            tenor_client.create_ns(ns_id,vnf_id,context['name'])
        return tenor_client.instantiate_ns(TenorId(ns_id))

api_v2.add_resource(ServiceInstances, '/service/instance')

# api_v1.add_resource(ServiceInstanceId, '/service/instance/<service_instance_id>')
# api_v1.add_resource(ServiceProjectId, '/service/instance/<service_instance_id>/state')

if __name__ == "__main__":
    print "Tablecloth (instances.controller v2 via TeNOR) ..."
    app.run(debug=True)
