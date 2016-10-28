#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, jsonify, request, Blueprint
import flask_restful
from flask_restful import Api, abort
from tenor_client.tenor_client import TenorClient
from tenor_client.tenor_dummy_id import TenorDummyId
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
PORT=8082
app = Flask(__name__)
api_v2_bp = Blueprint('api_v2', __name__)
api_v2 = Api(api_v2_bp)

tenor_client = TenorClient('http://localhost:4000')

class ServiceInstance(flask_restful.Resource):

    def get(self, ns_id=None):
        try:
            comp = tenor_client.get_ns_instances()
        except:
            abort(500,message="Error retrieving NS instances")
        resp = []
        for c in comp:
            ns_data = tenor_client.get_ns_instance_vnfs_status_addresses(c['id'])
            state = "UNKOWN"
            if ns_data[0]['state'] == 'ACTIVE':
                state = 'RUNNING'
            if ns_data[0]['state'] == 'SHUTOFF':
                state = 'DEPLOYED'
            if ns_data[0]['state'] == 'PROVISIONED':
                state = 'PROVISIONED'
            o = {'id': c['id'], 'service_instance_id': c['id'], 'state': state}
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
            if not 'bootstrap_script' in context:
                context['bootstrap_script'] = "#!/bin/bash"
            tenor_client.create_existing_vnf(vnf_id, context['vm_image'], context['name'],context['bootstrap_script'])
            tenor_client.create_existing_ns(ns_id, vnf_id, context['name'])
        else:
            tenor_client.create_vnf(vnf_id, context['vm_image'], context['name'])
            tenor_client.create_ns(ns_id, vnf_id, context['name'])
        data = tenor_client.instantiate_ns(TenorDummyId(ns_id))
        print data
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
        print data

    def get(self):
        data = request.get_json()
        print data

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
    app.run(debug=False, host='0.0.0.0', port=PORT)
