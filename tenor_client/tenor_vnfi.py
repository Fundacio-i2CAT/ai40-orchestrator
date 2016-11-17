#!/usr/bin/python
# -*- coding: utf-8 -*-
"""TeNOR Virtual Network Function Instance Representation Class and Client"""

import requests
import json
from jinja2 import Template
from tenor_dummy_id import TenorDummyId
from tenor_vnf import TenorVNF
import ConfigParser

CONFIG = ConfigParser.RawConfigParser()
CONFIG.read('config.cfg')

DEFAULT_TENOR_URL = format('{0}:{1}'.format(
    CONFIG.get('tenor', 'url'),
    CONFIG.get('tenor', 'port')))

class TenorVNFI(object):
    """Represents a TeNOR VNFI"""

    def __init__(self, vnfi_id,
                 tenor_url=DEFAULT_TENOR_URL):
        self._tenor_url = tenor_url
        self._vnfi_id = vnfi_id

    @staticmethod
    def get_vnfi_ids():
        """Returns the list of VNFIs registered in TeNOR"""
        try:
            print DEFAULT_TENOR_URL
            resp = requests.get('{0}/vnf-provisioning/vnf-instances'.format(DEFAULT_TENOR_URL))
        except:
            raise IOError('{0} instance unreachable'.format(DEFAULT_TENOR_URL))
        try:
            json.loads(resp.text)
        except:
            raise ValueError('Decoding VNF response json response failed')
        ids = []
        for vnfi in json.loads(resp.text):
            ids.append(vnfi['_id'])
        return ids

if __name__ == "__main__":
    print TenorVNFI.get_vnfi_ids()
