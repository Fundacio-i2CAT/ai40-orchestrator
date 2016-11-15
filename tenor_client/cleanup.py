#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests 
import json,ast
from jinja2 import Template
from tenor_dummy_id import TenorDummyId 
from pymongo import MongoClient

class TenorClient(object):

    def __init__(self,base_url='http://localhost:4000',
                 vnfd_template='./tenor_client/templates/min-f.json',
                 nsd_template='./tenor_client/templates/min-n.json',
                 existing_vnfd_template='./tenor_client/templates/singleip-f.json',
                 existing_nsd_template='./tenor_client/templates/singleip-n.json'):
        self._base_url = base_url

        with open(vnfd_template,'r') as f:
            self._f_template = Template(f.read())    

        with open(nsd_template,'r') as f:
            self._n_template = Template(f.read())    

        with open(existing_vnfd_template,'r') as f:
            self._ef_template = Template(f.read())    

        with open(existing_nsd_template,'r') as f:
            self._en_template = Template(f.read())    

    def create_existing_vnf(self,vnf_id,vm_image,name,bootstrap_script=None):
        """Creates a vnf using the already existing id in openstack"""
        script = "#!/bin/bash\n"
        if bootstrap_script:
            script = bootstrap_script
        rdata = self._ef_template.render(vnf_id=vnf_id,vm_image=vm_image,name=name,bootstrap_script=script)
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
    
    def instantiate_ns(self,ns_id=None,pop_id=None,callback_url='http://localhost:8082/orchestrator/api/v0.1/log',flavour='basic'):
        """Instantiates a ns on openstack, if no argument provided proceeds with the last one on the stack"""
        if not ns_id:
            nsds = self.get_ns()
            ns_id = self.get_last_ns_id()
        ns_data = {'ns_id': ns_id._id, 'pop_id': pop_id, 'callbackUrl': callback_url, 'flavour': flavour}
        response = requests.post('{0}/ns-instances'.format(self._base_url), 
                                 headers={'Content-Type': 'application/json'},
                                 json=ns_data)
        try:
            return json.loads(response.text)
        except:
            return { 'error' : response.text }
        
    def get_last_vnf_id(self):
        """Gets last vnf_id"""
        response = requests.get('{0}/vnfs'.format(self._base_url))
        vnfs = json.loads(response.text)
        ids = sorted([ x['vnfd']['id'] for x in vnfs ])
        if len(ids) == 0:
            return TenorDummyId(1899)
        ide = TenorDummyId(ids[-1])
        return ide

    def get_last_ns_id(self):
        """Gets last ns_id"""
        response = requests.get('{0}/network-services'.format(self._base_url))
        nss = json.loads(response.text)
        ids = sorted([ x['nsd']['id'] for x in nss ])
        if len(ids) == 0:
            return TenorDummyId(1899)
        ide = TenorDummyId(ids[-1])
        return ide
    
    def delete_ns_instance(self,ns_id):
        try:
            r = requests.delete('{0}/ns-instances/{1}'.format(self._base_url,ns_id))
            if r.status_code == 200:
                return { 'message': '{0} delete request successfully sent'.format(ns_id),
                         'status': 200 }
            else:
                return r.status_code 
        except:
            return 500

    def delete_all_ns(self):
        nss = self.get_ns()
        for ns in nss:
            requests.delete('{0}/network-services/{1}'.format(self._base_url,ns['nsd']['id']))
        return

    def delete_all_vnfs(self):
        vnfs = self.get_vnf()
        for vnf in vnfs:
            requests.delete('{0}/vnfs/{1}'.format(self._base_url,vnf['vnfd']['id']))
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

    def delete_all_ns_instances(self):
        ns_instances = self.get_ns_instances()
        for ns_instance in ns_instances:
            r = requests.delete('{0}/ns-instances/{1}'.format(self._base_url,ns_instance['id']))
        return

    def stop_ns(self,ns_tenor_id):
        """Stops an NS Instance ... shutoff all the VNF instances associated"""
        r = requests.put('{0}/ns-instances/{1}/stop'.format(self._base_url,ns_tenor_id))
        return r

    def start_ns(self,ns_tenor_id):
        """Starts an NS Instance ... sets active all the VNF instances associated"""
        r = requests.put('{0}/ns-instances/{1}/start'.format(self._base_url,ns_tenor_id))
        return r

    def get_ns_instance_vnfs_status_addresses(self,ns_instance_id):
        """Check status and addresses for vnfs associated to an ns"""
        response = requests.get('{0}/ns-instances/{1}'.format(self._base_url,ns_instance_id))
        try:
            data = json.loads(response.text)
        except:
            return [ {'state' : 'UNKNOWN'} ]
        status_addresses = []
        servers = []
        if not 'vnfrs' in data:
            return [ {'state': 'PROVISIONED'} ]
        for vnfr in data['vnfrs']:
            try:
                sta = { 'state': vnfr['server']['status'],
                        'addresses': [] }
                for ad in vnfr['server']['addresses']:
                    for ip in ad[1]:
                        sta['addresses'].append({'OS-EXT-IPS:type': ip['OS-EXT-IPS:type'], 'addr': ip['addr']})
                servers.append(sta)
            except:
                servers.append({'state': 'PROVISIONED'})
        if len(servers) > 0:
            return servers
        else:
            return [{'state': 'PROVISIONED'}]

if __name__ == '__main__':

    tc = TenorClient('http://localhost:4000')
    # a = TenorDummyId(u'2193')
    # print type(a+1)
    # print a+1
    # b = TenorDummyId(21938)
    # print type(b+1)
    # print b+1
    # print tc.get_vnf_instances()
    # tc.delete_all_ns_instances()
    # tc.delete_all_ns()
    # tc.delete_all_vnfs()
    client = MongoClient()
    ns_provisioning = client['ns_provisioning']
    ns_provisioning.nsrs.remove()
    vnf_provisioning = client['vnf_provisioning']
    vnf_provisioning.vnfrs.remove()
    ns_catalogue = client['ns_catalogue']
    ns_catalogue.ns.remove()
    vnf_catalogue = client['vnf_catalogue']
    vnf_catalogue.ns.remove()

    # print tc.get_ns_instance_vnfs_status_addresses('580861e7df67b5156e000000')
