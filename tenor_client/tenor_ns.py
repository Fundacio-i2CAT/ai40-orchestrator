#!/usr/bin/python
# -*- coding: utf-8 -*-
"""TeNOR Network Service Representation Class and Client"""

import requests
import json
from jinja2 import Template
from tenor_dummy_id import TenorDummyId
from tenor_vnf import TenorVNF
from tenor_vdu import TenorVDU

class TenorNS(object):
    """Represents a TeNOR NS"""

    def __init__(self, vnf,
                 tenor_url='http://localhost:4000'):
        self._dummy_id = None
        self._vnf = vnf
        self._tenor_url = tenor_url

    def get_last_ns_id(self):
        """Gets last ns_id"""
        try:
            response = requests.get('{0}/network-services'.format(self._tenor_url))
        except:
            raise IOError('TeNOR {0} instance unreachable'.format(self._tenor_url))
        try:
            nss = json.loads(response.text)
        except:
            raise ValueError('Decoding last_ns_id json response failed')
        ids = sorted([x['nsd']['id'] for x in nss])
        if len(ids) == 0:
            return TenorDummyId(1898)
        return TenorDummyId(ids[-1])

    def register(self, name, bootstrap_script=None):
        """Registers a NS via TeNOR"""
        self._dummy_id = self.get_last_ns_id
        self._vnf.register('NSINside',bootstrap_script='#!/bin/bash')

if __name__ == "__main__":

    VDU = TenorVDU()
    VNF = TenorVNF(VDU)
    NS = TenorNS(VNF)
    print NS.get_last_ns_id()
    NS.register("lkasjd")
