#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests 
import json,ast
from jinja2 import Template

class TenorId(object):
    """Manages mixed ids ... ints for vnfs and unicode for nsd"""
    def __init__(self,value):
        self._id = value
    
    def __add__(self,other):
        if type(self._id) is int:
            return str(self._id+other)
        elif type(self._id) is unicode:
            ords = [ ord(x) for x in self._id ]
            ords[-1] = ords[-1]+other
            ords[0] = ords[0]+other
            unis = [ unichr(x) for x in ords ]
            return ''.join(unis)

    def __repr__(self):
        return str(self._id)

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
        """Get the list of ns already created"""
        response = requests.get('{0}/network-services'.format(self._base_url))
        return json.loads(response.text)

    def get_configs_services(self):
        """Get the list of config services"""
        response = requests.get('{0}/configs/services'.format(self._base_url))
        return json.loads(response.text)

    def get_vnf(self):
        """Get the list of vnfs already created"""
        response = requests.get('{0}/vnfs'.format(self._base_url))
        return json.loads(response.text)

    def get_vnf_instances(self):
        """Get the list of vnfs already created"""
        response = requests.get('{0}/vnfs'.format(self._base_url))
        return json.loads(response.text)
        
    def instantiate_ns(self,ns_id=None,pop_id=None,callback_url="http://10.8.0.6",flavour="basic"):
        """Instantiates a ns on openstack, if no argument provided proceeds with the last one on the stack"""
        if not ns_id:
            nsds = self.get_ns()
            ns_id = self.get_last_ns_id()
        ns_data = {'ns_id': ns_id._id, 'pop_id': pop_id, "callbackUrl": callback_url, "flavour": flavour}
        
        response = requests.post('{0}/ns-instances'.format(self._base_url), 
                                 headers={'Content-Type': 'application/json'},
                                 json=ns_data)
        try:
            return json.loads(response.text)
        except:
            return { "error" : response.text }
        
    def get_last_vnf_id(self):
        """Gets last vnf_id"""
        response = requests.get('{0}/vnfs'.format(self._base_url))
        vnfs = json.loads(response.text)
        ids = sorted([ x['vnfd']['id'] for x in vnfs ])
        if len(ids) == 0:
            return TenorId(1899)
        ide = TenorId(ids[-1])
        return ide

    def get_last_ns_id(self):
        """Gets last ns_id"""
        response = requests.get('{0}/network-services'.format(self._base_url))
        nss = json.loads(response.text)
        ids = sorted([ x['nsd']['id'] for x in nss ])
        if len(ids) == 0:
            return TenorId(1899)
        ide = TenorId(ids[-1])
        return ide
    
    def delete_all_ns(self):
        nss = self.get_ns()
        for ns in nss:
            requests.delete("{0}/network-services/{1}".format(self._base_url,ns['nsd']['id']))
        return

    def delete_all_vnfs(self):
        vnfs = self.get_vnf()
        for vnf in vnfs:
            requests.delete("{0}/vnfs/{1}".format(self._base_url,vnf['vnfd']['id']))
        return

    def get_ns_instances(self,ns_instance_id=None):
        """Get the list of ns instances already created"""
        response = requests.get('{0}/ns-instances'.format(self._base_url))
        if not ns_instance_id:
            return json.loads(response.text)
        else:
            single = [ x for x in json.loads(response.text) if x['id'] == ns_instance_id ]
            return single
        return json.loads(response.text)

if __name__ == "__main__":
    tc = TenorClient("http://localhost:4000")
    # vnf_id = tc.get_last_vnf_id()+1
    # print tc.create_vnf(vnf_id,
    #                     "http://10.8.0.6/minimal.img",
    #                     "minimal-2")
    # print tc.create_ns(tc.get_last_ns_id()+1,
    #                    vnf_id,
    #                    "minimal-2")

    data = tc.get_ns_instances("580649cedf67b559d500000c")
    print json.dumps(data)

    # for x in data:
    #     print x['id']
    #     print 

    #    print json.dumps(tc.get_ns_instances("58063ba2df67b559d5000005"))

    # tc.delete_all_ns()
    # tc.delete_all_vnfs()

    # print tc.instantiate_ns()
    
    # print tc.create_existing_vnf("12000","0f5dd00c-7e99-4a33-b11f-0319b188e513","PXaaS")
    # print tc.create_existing_ns("12000","1200","PXaaS")
    # print tc.instantiate_ns()

    # print tc.create_vnf("122","http://10.8.0.6/minimal.img","minimal-2")
    # print tc.create_ns("122","122","minimal-2")
    # nsds = tc.get_ns()
    # ids = [ { 'id': x['nsd']['id'], 
    #           'oid': x['_id']['$oid'], 
    #           'vnfds': x['nsd']['vnfds'] } for x in nsds]
    # for nsd in ids:
    #     print ids
    # tc.instantiate_ns()
