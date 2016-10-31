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
            response = requests.get('{0}/vnfs'.format(self._tenor_url))
        except:
            raise IOError('TeNOR {0} instance unreachable'.format(self._tenor_url))
        try:
            vnfs = json.loads(response.text)
        except:
            raise ValueError('Decoding last_vnf_id json response failed')
        ids = sorted([x['vnfd']['id'] for x in vnfs])
        if len(ids) == 0:
            return TenorDummyId(1898)
        return TenorDummyId(ids[-1])

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
                                  name=name,
                                  bootstrap_script=bootstrap_script,
                                  storage_amount=self._vdu.storage_amount,
                                  vcpus=self._vdu.vcpus)
        try:
            response = requests.post('{0}/vnfs'.format(self._tenor_url),
                                     headers={'Content-Type': 'application/json'},
                                     json=json.loads(self._vnfd))
        except IOError:
            raise IOError('TeNOR {0} instance unreachable'.format(self._tenor_url))
        except ValueError:
            raise ValueError('Json encoding error registering VNF')
        try:
            json.loads(response.text)
        except:
            raise ValueError('Decoding new VNF response json response failed')
        return response

    def get_vdu(self):
        """Returns VNF associated VDU"""
        return self._vdu


if __name__ == "__main__":
    VDU = TenorVDU()
    VNF = TenorVNF(VDU)
    VNF.register("Prueba3")
