#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, jsonify, request, Blueprint
import flask_restful
from flask_restful import Api, abort
from tenor_client.tenor_client import TenorClient, TenorId
import requests
import json
from enums.final_state import FinalState
from database import mongodb
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
        api_dict = []
        api_dict.append({'uri': HEAD+'/', 'method': 'GET',
                          'purpose': 'REST API Structure'})
        api_dict.append({'uri': HEAD+'/service/instance', 'method': 'GET',
                          'purpose': 'Gets NS instances in TeNOR'})
        api_dict.append({'uri': HEAD+'/service/instance/<ns_id>', 'method': 'GET',
                          'purpose': 'Gets NS instance'})
        api_dict.append({'uri': HEAD+'/service/instance', 'method': 'POST',
                           'purpose': 'Registers and instantiates a stack on openstack via TeNOR'})
        return api_dict

class ServiceInstance(flask_restful.Resource):

    def get(self, ns_id=None):
        try:
            comp = tenor_client.get_ns_instances()
        except:
            abort(500,message="Error retrieving NS instances")
        resp = []
        for c in comp:
            ns_data = tenor_client.get_ns_instance_vnfs_status_addresses(c['id'])
            o = {'id': c['id'], 'service_instance_id': c['id'], 'state': ns_data[0]['state']}
            if 'addresses' in ns_data[0]:
                o['addresses'] = ns_data[0]['addresses']
            if ns_id:
                if c['id'] == ns_id:
                    return o
            else:
                resp.append(o)
        if len(resp) == 0:
            return []
        else:
            return resp

    def post(self, ns_id=None):
        data = request.get_json()
        context = data['context']['tenor']
        name = context['name']
        context_type = data['context_type']
        ns_id = tenor_client.get_last_ns_id()+1
        vnf_id = tenor_client.get_last_vnf_id()+1
        if context['vm_image_format'] == "openstack_id":
            tenor_client.create_existing_vnf(vnf_id, context['vm_image'], context['name'])
            tenor_client.create_existing_ns(ns_id, vnf_id, context['name'])
        else:
            tenor_client.create_vnf(vnf_id, context['vm_image'], context['name'])
            tenor_client.create_ns(ns_id, vnf_id, context['name'])
        data = tenor_client.instantiate_ns(TenorId(ns_id))
        try:
            return {'id': data['id'], 'service_instance_id': data['id'], 'state': 'PROVISIONED'}
        except:
            abort(500,message="Internal error")

    def put(self, ns_id=None):
        if not ns_id:
            abort(500,message="You should provide a NS id")
        state = request.get_json()
        ns_data = tenor_client.get_ns_instance_vnfs_status_addresses(ns_id)
        r = None
        try:
            if state['state'].upper() == 'START':
                r = tenor_client.start_ns(ns_id)
            if state['state'].upper() == 'STOP':
                r = tenor_client.stop_ns(ns_id)
            if state['state'].upper() == 'RUNNING':
                r = tenor_client.start_ns(ns_id)
            if state['state'].upper() == 'DEPLOYED':
                r = tenor_client.stop_ns(ns_id)
        except:
            abort(500,message='Internal server error')
        if r.status_code == 409:
            abort(409,message='{0} is stopped(running) can\'t stop(run) again'.format(ns_id))
        if r.status_code in (200, 201):
            return {'message': 'Successfully sent state signal'}
        else:
            abort(404,message='{0} NS not found'.format(ns_id))

    def delete(self, ns_id):
        if not ns_id:
            abort(500,message='No instance selected')
        else:
            r = tenor_client.delete_ns_instance(ns_id)
            if type(r) is int:
                abort(r,message='Error deleting {0}'.format(ns_id))
            else:
                return {'message': '{0} delete request successfully sent'.format(ns_id)}

class Log(flask_restful.Resource):

    def post(self):
        data = request.get_json()
        try:
            reponse = requests.get('http://192.168.10.70:8010/api/projects')
            print response
        except:
            print "Error forwarding callback"
        print data

    def get(self):
        data = request.get_json()
        try:
            reponse = requests.get('http://192.168.10.70:8010/api/projects')
            print response
        except:
            print "Error forwarding callback"
        print data

api_v2.add_resource(Root, '/')
api_v2.add_resource(Log, '/log')

api_v2.add_resource(ServiceInstance, 
                    '/service/instance',
                    '/service/instance/<ns_id>',
                    '/service/instance/<ns_id>/state')

if __name__ == "__main__":
    print "Tablecloth (instances.controller v2 via TeNOR) ..."
    app.register_blueprint(
        api_v2_bp,
        url_prefix='{prefix}/v{version}'.format(
            prefix=PREFIX,
            version=API_VERSION))
    app.run(debug=False, host='0.0.0.0', port=8082)
