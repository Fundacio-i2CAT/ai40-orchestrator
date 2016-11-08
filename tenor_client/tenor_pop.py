#!/usr/bin/python
# -*- coding: utf-8 -*-
"""TeNOR PoP Class"""

import requests
import json

DEFAULT_TENOR_URL = 'http://localhost:4000'

class TenorPoP(object):
    """Represents a TeNOR PoP"""

    def __init__(self, tenor_url=DEFAULT_TENOR_URL):
        pass

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
    print TenorPoP.get_pop_ids()
