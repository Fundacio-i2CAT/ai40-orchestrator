#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Anella 4.0 Orchestrator Tests"""

from start import PORT, URL_PREFIX
import json
import unittest
import requests
import random

BASE_URL = 'http://localhost:{0}{1}'.format(PORT, URL_PREFIX)

class OrchestratorTestCase(unittest.TestCase):
    """Full test"""

    def setUp(self):
        """Initial setup"""
        self._vnfs = []
        self._nss = []

    def test_02(self):
        """Gets NS instances"""
        resp = requests.get('{0}/service/instance'.format(BASE_URL))
        assert resp.status_code == 200
        instances = json.loads(resp.text)
        if len(instances) > 0:
            assert 'service_instance_id' in instances[0]
            for ins in instances:
                assert ins['state'].upper() in ('RUNNING', 'DEPLOYED', 'UNKNOWN')
        return instances

    def start_stop(self, prv, nxt, expected):
        """Aux. method to set prv state instances to nxt asserting expected status_code"""
        instances = self.test_02()
        f_instances = [x for x in instances if x['state'].upper() == prv]
        for ins in f_instances:
            url = '{0}/service/instance/{1}'.format(BASE_URL,
                                                    ins['service_instance_id'])
            resp = requests.put(url,
                                headers={'Content-Type': 'application/json'},
                                json={'state': nxt})
            assert resp.status_code == expected

    def test_03(self):
        """Testing start/stop"""
        self.start_stop('RUNNING', 'DEPLOYED', 200)
        self.start_stop('DEPLOYED', 'RUNNING', 200)

    def post_vnf(self, preserve=False):
        """Posts a new VNF"""
        with open('tenor_client/samples/ovnf_example.json') as infile:
            rdata = infile.read()
        url = '{0}/vnf'.format(BASE_URL)
        resp = requests.post(url, headers={'Content-Type': 'application/json'},
                             json=json.loads(rdata))
        assert resp.status_code == 200
        vnf_data = json.loads(resp.text)
        assert 'vnf_id' in vnf_data
        if not preserve:
            self._vnfs.append(vnf_data['vnf_id'])

    def post_ns(self, preserve=False):
        """Posts a new NS"""
        vresp = requests.get('{0}/vnf'.format(BASE_URL))
        assert vresp.status_code == 200
        vnf_data = json.loads(vresp.text)
        url = '{0}/ns'.format(BASE_URL)
        resp = requests.post(url, headers={'Content-Type': 'application/json'},
                             json={'vnf_id': random.choice(vnf_data)['vnf_id'],
                                   'name': 'randomTest'})
        assert resp.status_code == 200
        data = json.loads(resp.text)
        assert 'ns_id' in data
        if not preserve:
            self._nss.append(data['ns_id'])

    def test_04(self):
        """Posts VNFs"""
        self.post_vnf()
        self.post_vnf()

    def test_05(self):
        """Posts NSs"""
        self.post_vnf()
        self.post_vnf()
        self.post_vnf()
        self.post_vnf()
        self.post_ns()
        self.post_ns()

    def instantiate_ns(self):
        """Instantates a NS"""
        vresp = requests.get('{0}/ns'.format(BASE_URL))
        presp = requests.get('{0}/pop'.format(BASE_URL))
        pops = json.loads(presp.text)
        nss = json.loads(vresp.text)
        pop_id = pops[0]['pop_id']
        tns = random.choice(nss)
        ns_id = tns['ns_id']
        body = {'pop_id': pop_id,
                'callback_url': 'http://localhost:80',
                'config': [
                    {
                        'target_filename': '/var/www/html/index.html',
                        'content': '<h1>laksjdlaskjd</h1>'
                    }
                ]}
        url = '{0}/ns/{1}'.format(BASE_URL, ns_id)
        resp = requests.post(url,
                             headers={'Content-Type': 'application/json'},
                             json=body)
        assert resp.status_code == 200
        data = json.loads(resp.text)
        assert 'service_instance_id' in data
        assert data['state'].upper() == 'PROVISIONED'

    def test_06(self):
        """Posts vnf, ns and instantates it"""
        self.post_vnf(True)
        self.post_ns(True)
        self.instantiate_ns()

    def tearDown(self):
        """tearDown"""
        while len(self._nss) > 0:
            vnf = self._nss.pop()
            url = '{0}/ns/{1}'.format(BASE_URL, vnf)
            resp = requests.delete(url)
            assert resp.status_code == 200

        while len(self._vnfs) > 0:
            vnf = self._vnfs.pop()
            url = '{0}/vnf/{1}'.format(BASE_URL, vnf)
            resp = requests.delete(url)
            assert resp.status_code == 200

if __name__ == '__main__':
    unittest.main()
