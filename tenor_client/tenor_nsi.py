#!/usr/bin/python
# -*- coding: utf-8 -*-
"""TeNOR Network Service Instance Class and Client"""

import requests
import json

DEFAULT_TENOR_URL = 'http://localhost:4000'

class TenorNSI(object):
    """Represents a TeNOR NS Instance"""

    def __init__(self, nsid, tenor_url=DEFAULT_TENOR_URL):
        self._nsid = nsid
        self._tenor_url = tenor_url
        self._state = "UNKNOWN"
        self._addresses = []

    def __repr__(self):
        return "{0} {1} {2}".format(self._nsid,self._state,self._addresses)

    def retrieve(self):
        """Get NSI information from tenor instance"""
        try:
            response = requests.get('{0}/ns-instances'.format(self._tenor_url))
        except IOError:
            raise IOError('TeNOR {0} instance unreachable'.format(self._tenor_url))
        try:
            vnfs = json.loads(response.text)
        except:
            raise ValueError('Decoding last_vnf_id json response failed')
        nsis = [ x for x in json.loads(response.text) if x['id'] == self._nsid ]
        nsi = nsis[0]
        if 'vnfrs' in nsi:
            if len(nsi['vnfrs']) > 0:
                vnfr = nsi['vnfrs'][0]
                if 'server' in vnfr:
                    if vnfr['server']['status'].upper() == 'ACTIVE':
                        self._state = 'RUNNING'
                if vnfr['server']['status'].upper() == 'SHUTOFF':
                    self._state = 'DEPLOYED'
                self._addresses = vnfr['server']['addresses']
        return nsi

if __name__ == "__main__":
    NS = TenorNSI('5816fd72df67b518c3000000')
    hola = NS.retrieve()
    print NS
