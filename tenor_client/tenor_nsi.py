#!/usr/bin/python
# -*- coding: utf-8 -*-
"""TeNOR Network Service Instance Class and Client"""

import requests
import json
from pymongo import MongoClient
from pexpect import pxssh

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
            resp = requests.get('{0}/ns-instances/{1}'.format(
                self._tenor_url, self._nsid))
        except IOError:
            raise IOError('{0} instance unreachable'.format(self._tenor_url))
        try:
            nsi = json.loads(resp.text)
        except:
            self._state = 'UNKNOWN'
            return {}
        if 'vnfrs' in nsi:
            if len(nsi['vnfrs']) > 0:
                vnfr = nsi['vnfrs'][0]
                if 'server' in vnfr:
                    if 'status' in vnfr['server']:
                        if vnfr['server']['status'].upper() == 'ACTIVE':
                            self._state = 'RUNNING'
                        if vnfr['server']['status'].upper() == 'SHUTOFF':
                            self._state = 'DEPLOYED'
                    if 'addresses' in vnfr['server']:
                        self._addresses = vnfr['server']['addresses']
        return nsi

    def configure(self):
        """Configures the instance according to consumer needs"""
        server_ip = None
        for addr in self._addresses[0][1]:
            if addr['OS-EXT-IPS:type'].upper() == 'FLOATING':
                server_ip = addr['addr']
        client = MongoClient()
        mdb = client.custom_conf
        confs = mdb.confs
        config = confs.find_one({'ns_instance_id': self._nsid})
        session = pxssh.pxssh()
        session.login(server_ip, config['user'], config['password'])
        for cfile in config['config']:
            command = 'echo \'{0}\' > {1}'.format(cfile['content'].encode('latin-1'),
                                                  cfile['target_filename'])
            session.sendline(command)
            session.prompt(5)
        session.logout()

    def start(self):
        """Sets active all the VNF instances associated"""
        try:
            resp = requests.put('{0}/ns-instances/{1}/start'.format(
                self._tenor_url, self._nsid))
            self.retrieve()
        except:
            raise IOError('Error starting {0}'.format(self._nsid))
        return resp

    def stop(self):
        """Sets shutoff all the VNF instances associated"""
        try:
            resp = requests.put('{0}/ns-instances/{1}/stop'.format(
                self._tenor_url, self._nsid))
            self.retrieve()
        except:
            raise IOError('Error stoping {0}'.format(self._nsid))
        return resp

    def delete(self):
        """Deletes the NSI"""
        try:
            resp = requests.delete('{0}/ns-instances/{1}'.format(
                self._tenor_url, self._nsid))
        except IOError:
            raise IOError('Error deleting {0}'.format(self._nsid))
        return resp

    def get_state_and_addresses(self):
        """Returns state and addresses associated with the NSI"""
        addresses = []
        self.retrieve()
        for adr in self._addresses:
            for ipif in adr[1]:
                addresses.append({'OS-EXT-IPS:type': ipif['OS-EXT-IPS:type'],
                                  'addr': ipif['addr']})
        return {'service_instance_id': self._nsid,
                'state': self._state,
                'addresses': addresses}

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
            raise ValueError('Decoding NSI response json response failed')
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
