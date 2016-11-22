#!/usr/bin/python
# -*- coding: utf-8 -*-
"""TeNOR Network Service Instance Class and Client"""

import requests
import json
import paramiko
from pymongo import MongoClient
import uuid
from tenor_vnfi import TenorVNFI
from template_management import create_ssh_client
from template_management import render_template
from scp import SCPClient
import os
import ConfigParser

CONFIG = ConfigParser.RawConfigParser()
CONFIG.read('config.cfg')

DEFAULT_TENOR_URL = format('{0}:{1}'.format(
    CONFIG.get('tenor', 'url'),
    CONFIG.get('tenor', 'port')))

class TenorNSI(object):
    """Represents a TeNOR NS Instance"""

    def __init__(self, nsi_id, tenor_url=DEFAULT_TENOR_URL):
        self._nsi_id = nsi_id
        self._tenor_url = tenor_url
        self._state = "UNKNOWN"
        self._addresses = []
        self._image_id = None
        self.retrieve()

    def __repr__(self):
        return "{0} {1} {2}".format(self._nsi_id, self._state, self._addresses)

    def retrieve(self):
        """Get NSI information from tenor instance"""
        try:
            resp = requests.get('{0}/ns-instances/{1}'.format(
                self._tenor_url, self._nsi_id))
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
                if 'vnfr_id' in vnfr:
                    vnfi = TenorVNFI(vnfr['vnfr_id'])
                    self._image_id = vnfi.get_image_id()
                if 'server' in vnfr:
                    if 'status' in vnfr['server']:
                        if vnfr['server']['status'].upper() == 'ACTIVE':
                            self._state = 'RUNNING'
                        if vnfr['server']['status'].upper() == 'SHUTOFF':
                            self._state = 'DEPLOYED'
                    if 'addresses' in vnfr['server']:
                        self._addresses = vnfr['server']['addresses']
        return nsi

    def configure(self, server_ip=None, config=None):
        """Configures the instance according to consumer needs"""
        if not server_ip:
            for addr in self._addresses[0][1]:
                if addr['OS-EXT-IPS:type'].upper() == 'FLOATING':
                    server_ip = addr['addr']
        if not config:
            client = MongoClient()
            mdb = client.custom_conf
            confs = mdb.confs
            config = confs.find_one({'ns_instance_id': self._nsi_id})
            client.close()
        ssh = create_ssh_client(server_ip, 'root', 'keys/anella')
        scp = SCPClient(ssh.get_transport())
        if (not config) or (not 'config' in config):
            return
        for cfile in config['config']:
            filename = cfile['target_filename']
            if 'content' in cfile:
                content = cfile['content'].encode('utf-8')
                command = 'echo \'{0}\' > {1}'.format(content,
                                                      filename)
                print command
                stdin, stdout, stderr = ssh.exec_command(command)
                print stdout.readlines()
                print stderr.readlines()
            if 'context' in cfile:
                print 'Getting {0}'.format(filename)
                template_id = str(uuid.uuid4())
                template_filename = '/tmp/{0}'.format(template_id)
                scp.get(filename, template_filename)
                print 'Templating with {0}'.format(cfile['context'])
                result = render_template(template_id, cfile['context'])
                render_filename = '/tmp/{0}'.format(uuid.uuid4())
                with open(render_filename, 'w') as fhandle:
                    fhandle.write(result)
                print 'Sending {0}'.format(filename)
                scp.put(render_filename, filename)
                print 'Removing temporary files'
                os.remove(template_filename)
                os.remove(render_filename)
        print 'Closing ssh client'
        ssh.close()

    def start(self):
        """Sets active all the VNF instances associated"""
        try:
            resp = requests.put('{0}/ns-instances/{1}/start'.format(
                self._tenor_url, self._nsi_id))
            self.retrieve()
        except:
            raise IOError('Error starting {0}'.format(self._nsi_id))
        return resp

    def stop(self):
        """Sets shutoff all the VNF instances associated"""
        try:
            resp = requests.put('{0}/ns-instances/{1}/stop'.format(
                self._tenor_url, self._nsi_id))
            self.retrieve()
        except:
            raise IOError('Error stoping {0}'.format(self._nsi_id))
        return resp

    def delete(self):
        """Deletes the NSI"""
        try:
            resp = requests.delete('{0}/ns-instances/{1}'.format(
                self._tenor_url, self._nsi_id))
        except IOError:
            raise IOError('Error deleting {0}'.format(self._nsi_id))
        return resp

    def get_state_and_addresses(self):
        """Returns state and addresses associated with the NSI"""
        addresses = []
        self.retrieve()
        for adr in self._addresses:
            for ipif in adr[1]:
                addresses.append({'OS-EXT-IPS:type': ipif['OS-EXT-IPS:type'],
                                  'addr': ipif['addr']})
        if self._image_id:
            return {'service_instance_id': self._nsi_id,
                    'state': self._state,
                    'addresses': addresses,
                    'image_id': self._image_id}
        return {'service_instance_id': self._nsi_id,
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
    CONFIG = {'config': [
        {
            "target_filename": "/var/www/html/index.html",
            "context": {
                "name": "MONDAY",
                "picture": "https://cdn3.iconfinder.com/data/icons/users-6/100/2-512.png",
                "cv": "laksdj laskjd aslkjd "
            }
        },
        {
            "target_filename": "/root/customer_ip.txt",
            "content": "192.168.1.1"
        }
    ]
           }
    for n in NSS:
        NS = TenorNSI(n)
        print n
        print NS.get_state_and_addresses()
        NS.configure('172.24.4.207', CONFIG)
