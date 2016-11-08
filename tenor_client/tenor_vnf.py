#!/usr/bin/python
# -*- coding: utf-8 -*-
"""TeNOR Virtual Network Function Representation Class and Client"""

import requests
import json
from jinja2 import Template
from tenor_dummy_id import TenorDummyId
from tenor_vdu import TenorVDU

DEFAULT_TENOR_URL = 'http://localhost:4000'
DEFAULT_TEMPLATE = './tenor_client/templates/simple-f.json'

class TenorVNF(object):
    """Represents a TeNOR VNF"""

    def __init__(self, vdu,
                 tenor_url=DEFAULT_TENOR_URL,
                 template=DEFAULT_TEMPLATE):
        self._tenor_url = tenor_url
        self._template = template
        if type(vdu) is int:
            self.get_from_catalogue(vdu)
            self._dummy_id = vdu
        else:
            self._vdu = vdu
            self._dummy_id = None
            self._vnfd = None
            self._name = None

    def get_dummy_id(self):
        """Returns the TeNOR internal dummy_id"""
        return self._dummy_id

    def __repr__(self):
        return str(self._vnfd)

    def get_last_vnf_id(self):
        """Gets last vnf_id"""
        try:
            resp = requests.get('{0}/vnfs'.format(self._tenor_url))
        except:
            raise IOError('{0} instance unreachable'.format(self._tenor_url))
        try:
            vnfs = json.loads(resp.text)
        except:
            raise ValueError('Decoding last_vnf_id json resp failed')
        ids = sorted([x['vnfd']['id'] for x in vnfs])
        if len(ids) == 0:
            return TenorDummyId(1898)
        return TenorDummyId(ids[-1])

    def get_from_catalogue(self, vnf_id):
        """Gets the vnfd from TeNOR Catalogue"""
        try:
            resp = requests.get('{0}/vnfs'.format(self._tenor_url))
        except:
            raise IOError('{0} instance unreachable'.format(self._tenor_url))
        try:
            json.loads(resp.text)
        except:
            raise ValueError('Decoding last_vnf_id json resp failed')
        single = [x for x in json.loads(resp.text) if x['vnfd']['id'] == vnf_id]
        if len(single) > 0:
            self._vnfd = json.dumps(single[0])
            self._dummy_id = single[0]['vnfd']['id']
            return single[0]
        else:
            return None

    def delete(self):
        """Deletes the VNF from TeNOR"""
        try:
            resp = requests.delete('{0}/vnfs/{1}'.format(self._tenor_url,
                                                         self._dummy_id))
        except:
            raise IOError('{0} instance unreachable'.format(self._tenor_url))
        return

    def register(self, name, bootstrap_script=None):
        """Registers a VNF in TeNOR"""
        self._dummy_id = self.get_last_vnf_id()+1
        if not bootstrap_script:
            bootstrap_script = self._vdu.shell
        try:
            with open(self._template, 'r') as fhandle:
                templ = Template(fhandle.read())
        except:
            raise IOError('Template {0} IOError'.format(self._template))
        self._vnfd = templ.render(vnf_id=self._dummy_id,
                                  vm_image=self._vdu.vm_image,
                                  vm_image_format=self._vdu.vm_image_format,
                                  name=name,
                                  bootstrap_script=bootstrap_script,
                                  storage_amount=self._vdu.storage_amount,
                                  vcpus=self._vdu.vcpus)
        try:
            resp = requests.post('{0}/vnfs'.format(self._tenor_url),
                                 headers={'Content-Type': 'application/json'},
                                 json=json.loads(self._vnfd))
        except IOError:
            raise IOError('{0} instance unreachable'.format(self._tenor_url))
        except ValueError:
            raise ValueError('Json encoding error registering VNF')
        try:
            json.loads(resp.text)
        except:
            raise ValueError('Decoding new VNF resp json resp failed')
        return resp

    @staticmethod
    def get_vnf_ids():
        """Returns the list of VNF registered in TeNOR"""
        try:
            resp = requests.get('{0}/vnfs'.format(DEFAULT_TENOR_URL))
        except:
            raise IOError('{0} instance unreachable'.format(DEFAULT_TENOR_URL))
        try:
            json.loads(resp.text)
        except:
            raise ValueError('Decoding VNF response json response failed')
        ids = []
        for vnf in json.loads(resp.text):
            ids.append(vnf['vnfd']['id'])
        return ids

    def get_vdu(self):
        """Returns VNF associated VDU"""
        return self._vdu


if __name__ == "__main__":
    VDU = TenorVDU()
    VNF = TenorVNF(VDU)
    VNF.register("Prueba3")
    VNF = TenorVNF(1899)
    print VNF.get_dummy_id()
    print VNF
    print VNF.get_vnf_ids()
