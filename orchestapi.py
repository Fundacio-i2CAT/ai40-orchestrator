#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, jsonify, request, Blueprint
import flask_restful
from flask_restful import Api
from tenor_client.tenor_client import TenorClient,TenorId
import requests 
import json
from enums.final_state import FinalState
from database import mongodb
from common import response_json
from common.utils import add_validated_status
from bson.json_util import dumps
from bson import json_util
from common import parse_json

PREFIX = "/orchestrator/api"
API_VERSION = "0.1"
HEAD = PREFIX+'/v'+API_VERSION
app = Flask(__name__)
api_v2_bp = Blueprint('api_v2', __name__)
api_v2 = Api(api_v2_bp)

tenor_client = TenorClient('http://localhost:4000')

class Root(flask_restful.Resource):

    def get(self):
        api_dict = [ ]
        api_dict.append( { 'uri': HEAD+'/', 'method': 'GET', 
                           'purpose': 'REST API Structure' } )
        api_dict.append( { 'uri': HEAD+'/service/instance', 'method': 'GET', 
                           'purpose': 'Gets NS instances in TeNOR' } )
        api_dict.append( { 'uri': HEAD+'/service/instance/<ns_id>', 'method': 'GET', 
                           'purpose': 'Gets NS instance ' } )
        api_dict.append( { 'uri': HEAD+'/service/instance', 'method': 'POST', 
                           'purpose': 'Registers and instantiates a stack on openstack via TeNOR' } )
        return api_dict

class ServiceInstance(flask_restful.Resource):

    def get(self,ns_id=None):
        try:
            comp = tenor_client.get_ns_instances()
        except:
            return response_json.internal_server_error("Error retrieving")
        resp = []
        for c in comp:
            ns_data = tenor_client.get_ns_instance_vnfs_status_addresses(c['id'])
            o = { 'id': c['id'], 'instances': ns_data }
            if ns_id: 
                if c['id'] == ns_id:
                    return o
            else:
                resp.append(o)
        return resp

            
    def post(self,ns_id=None):
        data = request.get_json()
        context = data['context']['tenor']
        name = context['name']
        context_type = data['context_type']
        ns_id = tenor_client.get_last_ns_id()+1
        vnf_id = tenor_client.get_last_vnf_id()+1
        if context['vm_image_format'] == "openstack_id":
            tenor_client.create_existing_vnf(vnf_id,context['vm_image'],context['name'])
            tenor_client.create_existing_ns(ns_id,vnf_id,context['name'])
        else:
            tenor_client.create_vnf(vnf_id,context['vm_image'],context['name'])
            tenor_client.create_ns(ns_id,vnf_id,context['name'])
        data = tenor_client.instantiate_ns(TenorId(ns_id))
        try:
            return {'id': data['id'], 'state': 'PROVISIONED'}
        except:
            return response_json.internal_server_error("Error")

    def put(self,ns_id=None):
        if not ns_id:
            return response_json.internal_server_error("Error")
        state = request.get_json()
        r = None
        if state['state'].upper() == 'START':
            r = tenor_client.start_ns(ns_id)
        if state['state'].upper() == 'STOP':
            r = tenor_client.stop_ns(ns_id)
        if r.status_code == 409:
            return response_json.conflict_error('{0} is stopped(running) can\'t stop(run) again'.format(ns_id))
        return { 'message': 'OK', 'status': '200' }

    def delete(self,ns_id):
        if not ns_id:
            return response_json.internal_server_error('No instance selected')
        else:
            return tenor_client.delete_ns(ns_id)

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
    app.register_blueprint(
        api_v2_bp,
        url_prefix='{prefix}/v{version}'.format(
            prefix=PREFIX,
            version=API_VERSION))
    app.run(debug=True,host='0.0.0.0',port=8082)
