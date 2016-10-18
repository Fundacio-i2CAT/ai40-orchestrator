#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests 
import json,ast
from jinja2 import Template

class TenorClient(object):

    def __init__(self,base_url='http://localhost:4000',
                 vnfd_template='./tenor_client/templates/min-f.json',
                 nsd_template='./tenor_client/templates/min-n.json',
                 existing_vnfd_template='./tenor_client/templates/existing-f.json',
                 existing_nsd_template='./tenor_client/templates/existing-n.json'):
        self._base_url = base_url

        with open(vnfd_template,'r') as f:
            self._f_template = Template(f.read())    

        with open(nsd_template,'r') as f:
            self._n_template = Template(f.read())    

        with open(existing_vnfd_template,'r') as f:
            self._ef_template = Template(f.read())    

        with open(existing_nsd_template,'r') as f:
            self._en_template = Template(f.read())    

    def create_existing_vnf(self,vnf_id,vm_image,name):
        """Creates a vnf using the already existing id in openstack"""
        rdata = self._ef_template.render(vnf_id=vnf_id,vm_image=vm_image,name=name)
        response = requests.post('{0}/vnfs'.format(self._base_url), 
                                 headers={'Content-Type': 'application/json'},
                                 json=json.loads(rdata))
        return response.status_code

    def create_existing_ns(self,ns_id,vnf_id,name):
        """Creates a ns using the template corresponding to existing nsd"""
        rdata = self._en_template.render(ns_id=ns_id,vnf_id=vnf_id,name=name)
        response = requests.post('{0}/network-services'.format(self._base_url), 
                                 headers={'Content-Type': 'application/json'},
                                 json=json.loads(rdata))
        return response.status_code

    def create_vnf(self,vnf_id,vm_image,name):
        """Creates a vnf"""
        rdata = self._f_template.render(vnf_id=vnf_id,vm_image=vm_image,name=name)
        response = requests.post('{0}/vnfs'.format(self._base_url), 
                                 headers={'Content-Type': 'application/json'},
                                 json=json.loads(rdata))
        return response.status_code


    def create_ns(self,ns_id,vnf_id,name):
        """Creates a ns"""
        rdata = self._n_template.render(ns_id=ns_id,vnf_id=vnf_id,name=name)
        response = requests.post('{0}/network-services'.format(self._base_url), 
                                 headers={'Content-Type': 'application/json'},
                                 json=json.loads(rdata))
        return response.status_code

    def get_ns(self):
        """Get the lists of ns already created"""
        response = requests.get('{0}/network-services'.format(self._base_url))
        return json.loads(response.text)
        
    def instantiate_ns(self,ns_id=None,pop_id=None,callback_url="http://example.com",flavour="basic"):
        """Instantiates a ns on openstack, if no argument provided proceeds with the last one on the stack"""
        if not ns_id:
            nsds = self.get_ns()
            ns_id = nsds[-1]['nsd']['id']
        ns_data = {'ns_id': ns_id, 'pop_id': pop_id, "callbackUrl": callback_url, "flavour": flavour}
        response = requests.post('{0}/ns-instances'.format(self._base_url), 
                                 headers={'Content-Type': 'application/json'},
                                 json=ns_data)
        print response.text
        print response.status_code
        
if __name__ == "__main__":
    print "Tenor client demo"

    tc = TenorClient("http://localhost:4000")
    print tc.create_existing_vnf("124","6e23f9e5-d72c-48b1-94e2-7edff0d8adf5","minimal-2")
    print tc.create_existing_ns("124","124","minimal-2")
    print tc.instantiate_ns()

    # print tc.create_vnf("122","http://10.8.0.6/minimal.img","minimal-2")
    # print tc.create_ns("122","122","minimal-2")
    # nsds = tc.get_ns()
    # ids = [ { 'id': x['nsd']['id'], 
    #           'oid': x['_id']['$oid'], 
    #           'vnfds': x['nsd']['vnfds'] } for x in nsds]
    # for nsd in ids:
    #     print ids
    # tc.instantiate_ns()
