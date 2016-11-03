#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Anella 4.0 Orchestrator"""

from flask import Flask, Blueprint, request
import flask_restful
from flask_restful import Api, abort
import json
from tenor_client.tenor_vdu import TenorVDU
from tenor_client.tenor_vnf import TenorVNF
from tenor_client.tenor_ns import TenorNS
from tenor_client.tenor_nsi import TenorNSI
from pymongo import MongoClient
from pexpect import pxssh

PREFIX = "/orchestrator/api"
API_VERSION = "0.1"
PORT = 8082
APP = Flask(__name__)
API_V2_BP = Blueprint('api_v2', __name__)
API_V2 = Api(API_V2_BP)
DEFAULT_TENOR_URL = 'http://localhost:4000'

class VNF(flask_restful.Resource):
    """Virtual network function resources"""
    def __init__(self):
        pass

    def post(self):
        """Posts a new VNF"""
        data = request.get_json()
        vdu_data = data['vdu']
        vdu = TenorVDU(vdu_data['vm_image'],
                       vdu_data['vm_image_format'],
                       vdu_data['shell'],
                       vdu_data['storage_amount'],
                       vdu_data['vcpus'])
        vnf = TenorVNF(vdu)
        try:
            resp = vnf.register(data['name'])
        except Exception as exc:
            abort(500, message="Error registering VNF: {0}".format(str(exc)))
        try:
            data = json.loads(resp.text)
        except Exception as exc:
            abort(500,
                  message="Error decoding VNF reg.: {0}".format(str(exc)))
        return {'state': 'PROVISIONED', 'vnf_id': data['vnfd']['id']}

class NS(flask_restful.Resource):
    """Network service resources"""
    def __init__(self):
        pass

    def post(self, ns_id=None):
        """Posts a new NS"""
        if ns_id:
            try:
                data = request.get_json()
                vdu = TenorVDU()
                vnf = TenorVNF(vdu)
                tns = TenorNS(vnf)
                tns._dummy_id = ns_id
                resp = tns.instantiate()
                nsdata = json.loads(resp.text)
                client = MongoClient()
                db = client.custom_conf
                confs = db.confs
                confs.insert_one({'ns_instance_id': nsdata['id'],
                                  'user': data['user'],
                                  'password': data['password'],
                                  'config': data['config']})
                return {'service_instance_id': nsdata['id'],
                        'state': 'PROVISIONED'}
            except:
                abort(500, message='Error instantiating {0}'.format(ns_id))

        data = request.get_json()
        vnf_ids = TenorVNF.get_vnf_ids()
        if not data['vnf_id'] in vnf_ids:
            abort(404, message='vnf_id {0} not found'.format(data['vnf_id']))
        vnf = TenorVNF(data['vnf_id'])
        tns = TenorNS(data['vnf_id'])
        resp = tns.register(data['name'])
        try:
            data = json.loads(resp.text)
        except Exception as exc:
            abort(500,
                  message="Error decoding NS reg.: {0}".format(str(exc)))
        return {'state': 'PROVISIONED', 'ns_id': data['nsd']['id']}

class ServiceInstance(flask_restful.Resource):
    """Service instance resources"""
    def __init__(self):
        pass

    def get(self, ns_id=None):
        """Gets NSI information"""
        try:
            tids = TenorNSI.get_nsi_ids()
        except Exception as exc:
            abort(500,
                  message="Error retrieving NS instances: {0}".format(str(exc)))
        states = []
        for tid in tids:
            nsi = TenorNSI(tid)
            nsi_state = nsi.get_state_and_addresses()
            if ns_id:
                if tid == ns_id:
                    return nsi_state
            else:
                states.append(nsi_state)
        return states

    def post(self):
        """Post a new NSI"""
        data = request.get_json()
        context = data['context']['tenor']
        name = context['name']
        vdu = TenorVDU(context['vm_image'], context['vm_image_format'])
        if not 'bootstrap_script' in context:
            context['bootstrap_script'] = "#!/bin/bash"
        try:
            vnf = TenorVNF(vdu)
            tns = TenorNS(vnf)
            tns.register(name, context['bootstrap_script'])
            resp = tns.instantiate()
            nsdata = json.loads(resp.text)
        except Exception as exc:
            abort(500,
                  message="Error posting NS instance: {0}".format(str(exc)))
        return {'service_instance_id': nsdata['id'], 'state': 'PROVISIONED'}

    def put(self, ns_id=None):
        """Starting/Stopping NSIs"""
        if not ns_id:
            abort(500, message="You should provide a NS id")
        state = request.get_json()
        nsi = TenorNSI(ns_id)
        resp = None
        try:
            if state['state'].upper() == 'START':
                resp = nsi.start()
            if state['state'].upper() == 'STOP':
                resp = nsi.stop()
            if state['state'].upper() == 'RUNNING':
                resp = nsi.start()
            if state['state'].upper() == 'DEPLOYED':
                resp = nsi.stop()
        except Exception as exc:
            abort(500, message='Internal server error: {0}'.format(str(exc)))
        if hasattr(resp, 'status_code'):
            if resp.status_code == 409:
                abort(409,
                      message='Conflict: {0} stopped(running)'.format(ns_id))
            if resp.status_code in (200, 201):
                return {'message': 'Successfully sent state signal'}
            else:
                abort(404, message='{0} NS not found'.format(ns_id))
        else:
            abort(500,
                  message='Invalid state request: \'{0}\''.format(state['state'].upper()))

    def delete(self, ns_id):
        """Deletes NSIs"""
        if not ns_id:
            abort(500, message='No instance selected')
        else:
            try:
                nsi = TenorNSI(ns_id)
                nsi.delete()
                msg = '{0} request successfully sent'.format(ns_id)
                return {'message': msg}
            except Exception as exc:
                msg = 'Error deleting NS instance: {0}'.format(str(exc))
                abort(500, message=msg)

class Log(flask_restful.Resource):
    """TeNOR Logs"""
    def __init__(self):
        pass

    def post(self):
        """Log post"""
        # HANDLE CONSUMER CONFIGURATION HERE
        data = request.get_json()
        if 'descriptor_reference' in data:
            descriptor_reference = data['descriptor_reference']
            ns_instance_id = data['id']
            print "HOLA, SOY UN CALLBACK :)"
            print "LA INSTANCIA {0}".format(ns_instance_id)
            print "HA SIDO CREADA CON EL VNFD {0}".format(descriptor_reference)
            vnfr = data['vnfrs'][0]
            server_ip = None
            for addr in vnfr['server']['addresses'][0][1]:
                if addr['OS-EXT-IPS:type'].upper() == 'FLOATING':
                    server_ip = addr['addr']
            vnf = TenorVNF(int(data['descriptor_reference']))
            client = MongoClient()
            db = client.custom_conf
            confs = db.confs
            config = confs.find_one({'ns_instance_id': ns_instance_id})
            print config['user']
            print config['password']
            print config['config']
            print server_ip
            s = pxssh.pxssh()
            s.login(server_ip, config['user'], config['password'])
            for cfile in config['config']:
                command = 'echo \'{0}\' > {1}'.format(cfile['content'].encode('latin-1'), cfile['target_filename'])
                print command
                s.sendline(command)
                s.prompt(2)
            s.logout()
        # print "###############################################3333"
        # print "###############################################3333"
        # print "###############################################3333"
        # print json.dumps(data, indent=4, sort_keys=True)
        # print "###############################################3333"
        # print "###############################################3333"
        # print "###############################################3333"

    def get(self):
        """Log get"""
        data = request.get_json()

API_V2.add_resource(Log, '/log')
API_V2.add_resource(ServiceInstance,
                    '/service/instance',
                    '/service/instance/<ns_id>',
                    '/service/instance/<ns_id>/state')

API_V2.add_resource(VNF,
                    '/vnf')

API_V2.add_resource(NS,
                    '/ns',
                    '/ns/<ns_id>')

if __name__ == "__main__":
    print "Tablecloth (instances.controller v2 via TeNOR) ..."
    APP.register_blueprint(
        API_V2_BP,
        url_prefix='{prefix}/v{version}'.format(
            prefix=PREFIX,
            version=API_VERSION))
    APP.run(debug=True, host='0.0.0.0', port=PORT)
