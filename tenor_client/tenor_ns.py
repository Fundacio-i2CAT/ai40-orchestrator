#!/usr/bin/python
# -*- coding: utf-8 -*-
"""TeNOR Network Service Representation Class and Client"""

import requests
import json
from jinja2 import Template
from tenor_dummy_id import TenorDummyId
from tenor_vnf import TenorVNF
from tenor_vdu import TenorVDU

import ConfigParser

CONFIG = ConfigParser.RawConfigParser()
CONFIG.read('config.cfg')

DEFAULT_TENOR_URL = format('{0}:{1}'.format(
    CONFIG.get('tenor', 'url'),
    CONFIG.get('tenor', 'port')))

DEFAULT_TEMPLATE = './tenor_client/templates/simple-f.json'
DEFAULT_CALLBACK_URL = 'http://localhost:8082/orchestrator/api/v0.1/log'
DEFAULT_TEMPLATE = './tenor_client/templates/simple-n.json'
DEFAULT_FLAVOUR = 'basic'

class TenorNS(object):
    """Represents a TeNOR NS"""
    def __init__(self, vnf,
                 tenor_url=DEFAULT_TENOR_URL,
                 template=DEFAULT_TEMPLATE):
        self._template = template
        self._tenor_url = tenor_url
        self._dummy_id = None
        self._lite = False
        if type(vnf) is int:
            self._vnf = TenorVNF(vnf)
            self._lite = True
        else:
            self._vnf = vnf
        self._nsd = None

    def delete(self):
        """Deletes the NS"""
        url = '{0}/network-services/{1}'.format(self._tenor_url,
                                                self._dummy_id)
        try:
            resp = requests.delete(url)
        except:
            raise IOError('{0} instance unreachable'.format(self._tenor_url))
        return resp

    def get_last_ns_id(self):
        """Gets last ns_id"""
        try:
            resp = requests.get('{0}/network-services'.format(self._tenor_url))
        except:
            raise IOError('{0} instance unreachable'.format(self._tenor_url))
        try:
            nss = json.loads(resp.text)
        except:
            raise ValueError('Decoding last_ns_id json resp failed')
        ids = sorted([x['nsd']['id'] for x in nss])
        if len(ids) == 0:
            return TenorDummyId(1898)
        return TenorDummyId(ids[-1])

    def register(self, name, bootstrap_script=None):
        """Registers a NS via TeNOR"""
        self._dummy_id = self.get_last_ns_id()+1
        if self._lite == False:
            if not bootstrap_script:
                self._vnf.register(name,
                                   bootstrap_script=self._vnf.get_vdu().shell)
            else:
                self._vnf.register(name, bootstrap_script)
        try:
            with open(self._template, 'r') as fhandle:
                templ = Template(fhandle.read())
        except:
            raise IOError('Template {0} IOError'.format(self._template))
        self._nsd = templ.render(ns_id=self._dummy_id,
                                 vnf_id=self._vnf.get_dummy_id(),
                                 flavor=self._vnf.get_vdu().flavor,
                                 name=name)
        try:
            resp = requests.post('{0}/network-services'.format(self._tenor_url),
                                 headers={'Content-Type': 'application/json'},
                                 json=json.loads(self._nsd))
            return resp
        except IOError:
            raise IOError('{0} instance unreachable'.format(self._tenor_url))
        except ValueError:
            raise ValueError('Json encoding error registering NSD')
        try:
            json.loads(resp.text)
        except:
            raise ValueError('Decoding new NS resp json resp failed')
        return resp

    def instantiate(self,
                    pop_id=None,
                    public_network_id=None,
                    callback_url=DEFAULT_CALLBACK_URL,
                    flavour=DEFAULT_FLAVOUR):
        """Instantiates the NS on openstack"""
        ns_data = {'ns_id': self._dummy_id, 'pop_id': pop_id,
                   'callbackUrl': callback_url, 'flavour': flavour, 
                   'public_network_id': public_network_id}
        print ns_data
        try:
            resp = requests.post('{0}/ns-instances'.format(self._tenor_url),
                                 headers={'Content-Type': 'application/json'},
                                 json=ns_data)
        except IOError:
            raise IOError('{0} instance unreachable'.format(self._tenor_url))
        except ValueError:
            raise ValueError('Json encoding error instantiating NS')
        try:
            json.loads(resp.text)
        except:
            raise ValueError('Decoding new NSI resp json resp failed')
        return resp

    def set_dummy_id(self, dummy_id):
        """Sets dummy_id"""
        self._dummy_id = dummy_id

    @staticmethod
    def get_ns_ids():
        """Returns the list of NS registered in TeNOR"""
        url = '{0}/network-services'.format(DEFAULT_TENOR_URL)
        try:
            resp = requests.get(url)
        except:
            raise IOError('{0} instance unreachable'.format(DEFAULT_TENOR_URL))
        try:
            json.loads(resp.text)
        except:
            raise ValueError('Decoding NS response json response failed')
        ids = []
        for tns in json.loads(resp.text):
            ids.append(tns['nsd']['id'])
        return ids


if __name__ == "__main__":
    VDU = TenorVDU()
    VNF = TenorVNF(VDU)
    NS = TenorNS(VNF)
    print NS.get_last_ns_id()
    print NS.register("Test")
    NS.delete()
