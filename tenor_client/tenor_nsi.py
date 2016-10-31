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
        self.retrieve()

    def __repr__(self):
        return "{0} {1} {2}".format(self._nsid, self._state, self._addresses)

    def retrieve(self):
        """Get NSI information from tenor instance"""
        try:
            response = requests.get('{0}/ns-instances'.format(self._tenor_url))
        except IOError:
            raise IOError('{0} instance unreachable'.format(self._tenor_url))
        try:
            json.loads(response.text)
        except:
            raise ValueError('Decoding last_vnf_id json response failed')
        nsis = [x for x in json.loads(response.text) if x['id'] == self._nsid]
        try:
            nsi = nsis[0]
        except:
            raise ValueError('NSI {0} not found'.format(self._nsid))
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

    def get_state_and_addresses(self):
        """Returns state and addresses associated with the NSI"""
        addresses = []
        for adr in self._addresses:
            for ipif in adr[1]:
                addresses.append({'OS-EXT-IPS:type': ipif['OS-EXT-IPS:type'],
                                  'addr': ipif['addr']})
        return {'state': self._state, 'addresses': addresses}

    @staticmethod
    def get_nsi_ids():
        """Returns the list of NSI registered in TeNOR"""
        try:
            resp = requests.get('{0}/ns-instances'.format(DEFAULT_TENOR_URL))
        except:
            raise IOError('{0} instance unreachable'.format(DEFAULT_TENOR_URL))
        try:
            json.loads(resp.text)
        except:
            raise ValueError('Decoding new NS response json response failed')
        ids = []
        for nsi in json.loads(resp.text):
            ids.append(nsi['id'])
        return ids

if __name__ == "__main__":
    NSS = TenorNSI.get_nsi_ids()
    for n in NSS:
        NS = TenorNSI(n)
        print n
        print NS.get_state_and_addresses()
