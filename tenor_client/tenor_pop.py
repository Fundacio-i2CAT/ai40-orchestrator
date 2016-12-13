#!/usr/bin/python
# -*- coding: utf-8 -*-
"""TeNOR PoP Class"""

import requests
import json

DEFAULT_TENOR_URL = 'http://localhost:4000'

class TenorPoP(object):
    """Represents a TeNOR PoP"""

    def __init__(self, pop_id=None, tenor_url=DEFAULT_TENOR_URL):
        self._pop_id = pop_id

    def get_name(self):
        url = '{0}/pops/dc/{1}'.format(DEFAULT_TENOR_URL,self._pop_id)
        try:
            resp = requests.get(url)
        except:
            raise IOError('{0} instance unreachable'.format(DEFAULT_TENOR_URL))
        try:
            json.loads(resp.text)
        except:
            raise ValueError('Decoding PoP response json response failed')
        ids = []
        pop = json.loads(resp.text)
        return pop['name']

    def get_network_details(self):
        url = '{0}/pops/networks/{1}'.format(DEFAULT_TENOR_URL,self._pop_id)
        try:
            resp = requests.get(url)
        except:
            raise IOError('{0} PoP unreachable'.format(self._pop_id))
        try:
            networks = json.loads(resp.text)
        except:
            raise ValueError('Decoding PoP response json response failed')
        network_details = []
        for network in networks["networks"]:
            network_details.append({'name': network['name'],
                                   'id': network['id'],
                                   'router_external': network['router:external']})
        return network_details

    def get_flavor_details(self):
        url = '{0}/pops/flavours/{1}'.format(DEFAULT_TENOR_URL,self._pop_id)
        try:
            resp = requests.get(url)
        except:
            raise IOError('{0} PoP unreachable'.format(self._pop_id))
        try:
            flavors = json.loads(resp.text)
        except:
            raise ValueError('Decoding PoP response json response failed')
        flavor_details = []
        for flavor in flavors["flavors"]:
            flavor_details.append({'name': flavor['name'],
                                   'ram': flavor['ram'],
                                   'disk': flavor['disk'],
                                   'vcpus': flavor['vcpus']})
        return flavor_details

    @staticmethod
    def get_pop_ids():
        """Gets the list of PoP registered"""
        url = '{0}/pops/dc'.format(DEFAULT_TENOR_URL)
        try:
            resp = requests.get(url)
        except:
            raise IOError('{0} instance unreachable'.format(DEFAULT_TENOR_URL))
        try:
            json.loads(resp.text)
        except:
            raise ValueError('Decoding PoP response json response failed')
        ids = []
        for pop in json.loads(resp.text):
            ids.append(pop['id'])
        return ids

if __name__ == "__main__":
    POP = TenorPoP()
    IDS = TenorPoP().get_pop_ids()
    POPI = TenorPoP(1)
    print POPI.get_flavor_details()
