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
from tenor_client.tenor_pop import TenorPoP
from pymongo import MongoClient
import ConfigParser
import datetime

CONFIG = ConfigParser.RawConfigParser()
CONFIG.read('config.cfg')
POP_ID = int(CONFIG.get('tenor','default_pop'))

HOST = CONFIG.get('flask', 'host')
PREFIX = CONFIG.get('flask', 'prefix')
API_VERSION = CONFIG.get('flask', 'version')
PORT = int(CONFIG.get('flask', 'port'))
APP = Flask(__name__)
API_V2_BP = Blueprint('api_v2', __name__)
API_V2 = Api(API_V2_BP)
DEFAULT_TENOR_URL = format('{0}:{1}'.format(
    CONFIG.get('tenor', 'url'),
    CONFIG.get('tenor', 'port')))
URL_PREFIX = '{prefix}/v{version}'.format(
    prefix=PREFIX,
    version=API_VERSION)
BASE_URL = 'http://localhost:{0}{1}'.format(PORT, URL_PREFIX)

class VNF(flask_restful.Resource):
    """Virtual network function resources"""
    def __init__(self):
        pass

    def delete(self, vnf_id):
        """Deletes a VNF"""
        vnf = TenorVNF(int(vnf_id))
        try:
            vnf.delete()
        except Exception as exc:
            abort(500, message="Error deleting VNF: {0}".format(str(exc)))
        return {'message': 'successfully deleted'}

    def get(self, vnf_id=None):
        """Gets VNF(s)"""
        ids = TenorVNF.get_vnf_ids()
        result = []
        if vnf_id:
            for vid in ids:
                if vid == int(vnf_id):
                    return {'vnf_id': vid}
            abort(404, message='{0} VNF not found'.format(vnf_id))
        for vnf_sid in ids:
            result.append({'vnf_id': vnf_sid})
        return result

    def post(self):
        """Posts a new VNF"""
        data = request.get_json()
        vdu_data = data['vdu']
        cached = "false"
        if 'cached' in vdu_data:
            cached = vdu_data['cached']
        if cached:
            cached = "true"
        vdu = TenorVDU(vdu_data['vm_image'],
                       vdu_data['vm_image_format'],
                       vdu_data['flavor'],
                       cached,
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

    def get(self, ns_id=None):
        """Gets NS(s)"""
        ids = TenorNS.get_ns_ids()
        result = []
        if ns_id:
            for nid in ids:
                if nid == ns_id:
                    return {'ns_id': int(nid)}
            abort(404, message='{0} NS not found'.format(ns_id))
        for ns_sid in ids:
            result.append({'ns_id': int(ns_sid)})
        return result

    def delete(self, ns_id):
        """Deletes a NS"""
        vdu = TenorVDU()
        vnf = TenorVNF(vdu)
        tns = TenorNS(vnf)
        tns.set_dummy_id(ns_id)
        try:
            resp = tns.delete()
        except Exception as exc:
            abort(500, message="Error deleting NS: {0}".format(str(exc)))
        if resp.status_code == 200:
            return {'message': 'successfully deleted'}
        else:
            abort(resp.status_code,
                  message='Error deleting {0} ns'.format(ns_id))

    def post(self, ns_id=None):
        """Posts a new NS"""
        if ns_id:
            try:
                data = request.get_json()
                vdu = TenorVDU()
                vnf = TenorVNF(vdu)
                tns = TenorNS(vnf)
                tns.set_dummy_id(ns_id)
                if not 'pop_id' in data:
                    abort(400, message='Lack of PoP id')
                available_pops = TenorPoP().get_pop_ids()
                if not data['pop_id'] in available_pops:
                    abort(404, message='PoP {0} not found'.format(data['pop_id']))
                resp = tns.instantiate(data['pop_id'])
                nsdata = json.loads(resp.text)
                client = MongoClient()
                mdb = client.custom_conf
                confs = mdb.confs
                if not 'user' in data:
                    data['user'] = None
                    data['password'] = None
                confs.insert_one({'ns_instance_id': nsdata['id'],
                                  'user': data['user'],
                                  'password': data['password'],
                                  'consumer_params': data['context']['consumer_params']})
                client.close()
                return {'service_instance_id': nsdata['id'],
                        'state': 'PROVISIONED'}
            except:
                nsi = TenorNSI(ns_id)
                nsi.delete()
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

class PoP(flask_restful.Resource):
    """PoP related resources"""
    def __init__(self):
        pass

    def get(self, pop_id=None, resource=None):
        ids = TenorPoP.get_pop_ids()
        result = []
        if pop_id:
            for pid in ids:
                if pid == int(pop_id):
                    tpop = TenorPoP(pid)
                    if not resource:
                        return {'pop_id': pop_id, 'name': tpop.get_name()}
                    if resource == 'flavors':
                        return {'flavors': tpop.get_flavor_details()}
                    elif resource == 'networks':
                        return {'networks': tpop.get_network_details()}
            if resource:
                abort(404, message='{0} PoP not found or resource {1} not in (networks,flavors)'.format(pop_id,resource))
        for pop_sid in ids:
            my_pop = TenorPoP(pop_sid)
            result.append({'pop_id': pop_sid,
                           'name': my_pop.get_name()})
        return result

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
        log_db_client = MongoClient()
        log_db = log_db_client.orchestrator_logs
        logs = log_db.logs
        logs.insert_one({'method': 'POST',
                         'request': data,
                         'date': datetime.datetime.utcnow()})
        log_db_client.close()
        context = data['context']
        name = context['name_image']
        cached = "true"
        if 'cached' in context:
            cached = context['cached']
        if cached:
            cached = "true"
        vdu = TenorVDU(context['vm_image'], context['vm_image_format'],
                       context['flavor'],cached)
        if not 'bootstrap_script' in context:
            shell = None
            with open('keys/anella.json') as data_file:
                shell = json.load(data_file)
            context['bootstrap_script'] = shell['shell']
        try:
            vnf = TenorVNF(vdu)
            tns = TenorNS(vnf)
            tns.register(name, context['bootstrap_script'])
            resp = None
            pop_id = POP_ID
            if 'pop_id' in context:
                pop_id = context['pop_id']
            if not 'public_network_id' in context:
                resp = tns.instantiate(pop_id)
            else:
                print context['public_network_id']
                resp = tns.instantiate(pop_id, context['public_network_id'])
            nsdata = json.loads(resp.text)
        except Exception as exc:
            abort(500,
                  message="Error posting NS instance: {0}".format(str(exc)))
        client = MongoClient()
        mdb = client.custom_conf
        confs = mdb.confs
        if not 'user' in data:
            data['user'] = None
            data['password'] = None
        if 'consumer_params' in data['context']:
            confs.insert_one({'ns_instance_id': nsdata['id'],
                              'user': data['user'],
                              'password': data['password'],
                              'consumer_params': data['context']['consumer_params']})
        client.close()
        return {'service_instance_id': nsdata['id'], 'state': 'PROVISIONED'}

    def put(self, ns_id=None):
        """Starting/Stopping NSIs"""
        if not ns_id:
            abort(500, message="You should provide a NS id")
        state = request.get_json()
        log_db_client = MongoClient()
        log_db = log_db_client.orchestrator_logs
        logs = log_db.logs
        logs.insert_one({'method': 'PUT',
                         'request': state,
                         'date': datetime.datetime.utcnow()})
        log_db_client.close()
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
                print resp.text
                abort(404, message='{0} NS not found'.format(ns_id))
        else:
            abort(500,
                  message='Invalid: \'{0}\''.format(state['state'].upper()))

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
        data = request.get_json()
        # print "#############################"
        # print json.dumps(data, indent=4, sort_keys=True)
        # print "#############################"
        if 'descriptor_reference' in data:
            ns_instance_id = data['id']
            nsi = TenorNSI(ns_instance_id)
            nsi.configure()

    def get(self):
        """Log get"""
        data = request.get_json()
        return data

API_V2.add_resource(Log, '/log')
API_V2.add_resource(ServiceInstance,
                    '/service/instance',
                    '/service/instance/<ns_id>',
                    '/service/instance/<ns_id>/state')

API_V2.add_resource(VNF,
                    '/vnf',
                    '/vnf/<vnf_id>')

API_V2.add_resource(NS,
                    '/ns',
                    '/ns/<ns_id>')

API_V2.add_resource(PoP,
                    '/pop',
                    '/pop/<pop_id>',
                    '/pop/<pop_id>/<resource>')

if __name__ == "__main__":
    print "Industrial Platform 4.0 Orchestrator"
    APP.register_blueprint(
        API_V2_BP,
        url_prefix=URL_PREFIX
    )
    APP.run(debug=True, host=HOST, port=PORT)
