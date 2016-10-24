#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, jsonify, request, Blueprint
import flask_restful
from flask_restful import Api
from tenor_client import TenorClient,TenorId
import requests 
import json
import sys
sys.path.append("./enums/")
from final_state import FinalState

app = Flask(__name__)
api_v2_bp = Blueprint('api_v2', __name__)
api_v2 = Api(api_v2_bp)

tenor_client = TenorClient('http://localhost:4000')

class Root(flask_restful.Resource):

    def get(self):
        api_dict = [ ]
        api_dict.append( { "uri": "/", "method": "GET", 
                           "purpose": "REST API Structure" } )
        api_dict.append( { "uri": "/service/instance", "method": "GET", 
                           "purpose": "Gets NS instances in TeNOR" } )
        api_dict.append( { "uri": "/service/instance/<ns_id>", "method": "GET", 
                           "purpose": "Gets NS instance " } )
        api_dict.append( { "uri": "/service/instance", "method": "POST", 
                           "purpose": "Registers and instantiates a stack on openstack via TeNOR" } )
        return api_dict

class ServiceInstance(flask_restful.Resource):

    def get(self,ns_id=None):
        if ns_id:
            return tenor_client.get_ns_instance_vnfs_status_addresses(ns_id)
        return tenor_client.get_ns_instances()

    def post(self,ns_id=None):
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

    def put(self,ns_id=None):
        if not ns_id:
            return "404"
        state = request.get_json()
        r = None
        if state['state'].upper() == 'START':
            r = tenor_client.start_ns(ns_id)
        if state['state'].upper() == 'STOP':
            r = tenor_client.stop_ns(ns_id)
        return r.status_code

api_v2.add_resource(Root, '/')
api_v2.add_resource(ServiceInstance, 
                    '/service/instance',
                    '/service/instance/<ns_id>',
                    '/service/instance/<ns_id>/state',
                    endpoint='user')

# api_v1.add_resource(ServiceInstanceId, '/service/instance/<service_instance_id>')
# api_v1.add_resource(ServiceProjectId, '/service/instance/<service_instance_id>/state')

if __name__ == "__main__":
    print "Tablecloth (instances.controller v2 via TeNOR) ..."
    PREFIX = "/orchestrator/api"
    API_VERSION = "0.1"
    app.register_blueprint(
        api_v2_bp,
        url_prefix='{prefix}/v{version}'.format(
            prefix=PREFIX,
            version=API_VERSION))
    app.run(debug=True,host='0.0.0.0',port=8081)
