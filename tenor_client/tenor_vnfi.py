#!/usr/bin/python
# -*- coding: utf-8 -*-
"""TeNOR Virtual Network Function Instance Representation Class and Client"""

import requests
import json
import ConfigParser

CONFIG = ConfigParser.RawConfigParser()
CONFIG.read('config.cfg')

DEFAULT_TENOR_URL = format('{0}:{1}'.format(
    CONFIG.get('tenor', 'url'),
    CONFIG.get('tenor', 'port')))

class TenorVNFI(object):
    """Represents a TeNOR VNFI"""

    def __init__(self, vnfi_id=None,
                 tenor_url=DEFAULT_TENOR_URL):
        self._tenor_url = tenor_url
        self._image_id = None
        self._vnfi_id = vnfi_id
        self._all = None
        if self._vnfi_id:
            self.retrieve()

    def retrieve(self):
        """Get VNFI information from tenor instance"""
        try:
            resp = requests.get(
                '{0}/vnf-provisioning/vnf-instances/{1}'.format(
                self._tenor_url, self._vnfi_id))
        except IOError:
            raise IOError('{0} VNFI unreachable'.format(self._tenor_url))
        try:
            vnfi = json.loads(resp.text)
        except:
            raise ValueError('Decoding VNFI response json response failed')
        self._all = resp.text
        vms = vnfi['vms']
        if len(vms) > 0:
            if 'image_id' in vms[0]:
                self._image_id = vms[0]['image_id']
        return self._image_id

    def get_image_id(self):
        """Getter"""
        return self._image_id

    @staticmethod
    def get_vnfi_ids():
        """Returns the list of VNFIs registered in TeNOR"""
        try:
            url = '{0}/vnf-provisioning/vnf-instances'.format(DEFAULT_TENOR_URL)
            resp = requests.get(url)
        except:
            raise IOError('{0} instance unreachable'.format(DEFAULT_TENOR_URL))
        try:
            json.loads(resp.text)
        except:
            raise ValueError('Decoding VNFI response json response failed')
        ids = []
        for vnfi in json.loads(resp.text):
            ids.append(vnfi['_id'])
        return ids

if __name__ == "__main__":
    IDS = TenorVNFI.get_vnfi_ids()
    if len(IDS) > 0:
        VNFI = TenorVNFI(IDS[0])
        HOLA = json.loads(VNFI._all)
        print json.dumps(HOLA, indent=4, sort_keys=True)
        print VNFI.get_image_id()
