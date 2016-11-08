#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Anella 4.0 Orchestrator Tests"""

from start import PORT, URL_PREFIX
import json
import unittest
import requests
import threading
import functools

BASE_URL = 'http://dev.anella.i2cat.net:{0}{1}'.format(PORT, URL_PREFIX)

class OrchestratorTestCase(unittest.TestCase):
    """Full test"""

    def setUp(self):
        """Initial setup"""
        pass

    def step1(self):
        """Post NS instance"""
        with open('tenor_client/samples/another.json') as infile:
            rdata = infile.read()
        # resp = requests.post('{0}/service/instance'.format(BASE_URL),
        #               headers={'Content-Type': 'application/json'},
        #               json=json.loads(rdata))
        # assert resp.status_code == 200
        # data = json.loads(resp.text)
        # assert 'service_instance_id' in data
        # assert data['state'].upper() == 'PROVISIONED'

    def step2(self):
        """Gets NS instances"""
        resp = requests.get('{0}/service/instance'.format(BASE_URL))
        assert resp.status_code == 200
        instances = json.loads(resp.text)
        if len(instances) > 0:
            assert 'service_instance_id' in instances[0]
        return instances

    def step3(self):
        """Stops all NS instances"""
        instances = self.step2()
        running_instances = [x for x in instances if x['state'].upper() == 'RUNNING']
        for ins in running_instances:
            url = '{0}/service/instance/{1}'.format(BASE_URL,
                                                    ins['service_instance_id'])
            stop_resp = requests.put(url,
                                     headers={'Content-Type': 'application/json'},
                                     json={'state': 'deployed'})
            assert stop_resp.status_code == 200

    def step4(self):
        """Starts all NS stopped instances"""
        instances = self.step2()
        deployed_instances = [x for x in instances if x['state'].upper() == 'DEPLOYED']
        for ins in deployed_instances:
            url = '{0}/service/instance/{1}'.format(BASE_URL,
                                                    ins['service_instance_id'])
            start_resp = requests.put(url,
                                     headers={'Content-Type': 'application/json'},
                                     json={'state': 'start'})
            assert start_resp.status_code == 200

    def step5(self):
        """Posts a new VNF"""
        pass
        

    def _steps(self):
        """Steps"""
        for name in sorted(dir(self)):
            if name.startswith("step"):
                yield name, getattr(self, name)

    def test_steps(self):
        """Sorting steps"""
        for name, step in self._steps():
            print name, step.__doc__
            try:
                step()
            except Exception as exc:
                self.fail("{} {} failed ({}: {})".format(name, step.__doc__, type(exc), exc))

if __name__ == '__main__':
    unittest.main()
