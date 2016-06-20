import abc
import requests
import paramiko
#from common.config_parser import URL_CATALOG_CONTEXT
from flask import jsonify
import json


class SimpleLifeCicleManager(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def getCurrentState(self, service_description_id):
        raise NotImplementedError("Please Implement this method")

    @abc.abstractmethod
    def setDesiredState(self, state):
        raise NotImplementedError("Please Implement this method")


class SimpleLifeCicleManagerImpl(SimpleLifeCicleManager):
    def setDesiredState(self, state):
        pass

    def getCurrentState(self, service_project_id):
        get_context(service_project_id)

        #connect_paramiko()


def get_context(service_project_id):
    # Connect to BBDD . Get Context
    #result = requests.get(URL_CATALOG_CONTEXT + service_project_id)
    result = requests.get('http://0.0.0.0:8080/catalog/api/v0.1/service/context/' + service_project_id)
    data = json.loads(result.text)
    print data.get('_id')


def connect_paramiko():
    ssh = None
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh.connect(hostname='192.168.10.175', username='vmubuntu', password='vm1234', port=22)
        transport = ssh.get_transport()
        session = transport.open_session()
        session.set_combine_stderr(True)
        session.get_pty()
        #session.exec_command("sudo systemctl stop apache2.service")
        #session.exec_command("sudo systemctl is-active apache2.service")
        stdin = session.makefile('wb', -1)
        stdout = session.makefile('rb', -1)
        stdin.write('vm1234' + '\n')
        stdin.flush()
        print stdout.read()
        if stdout.channel.recv_exit_status() is 0:
            return 0
        else:
            return -1

    finally:
        if ssh is not None:
            ssh.close()

if __name__ == "__main__":
    slcm = SimpleLifeCicleManagerImpl()
    slcm.getCurrentState("5763c9cf7224e48c11b57eea")
