import paramiko
from common.utils import get_state_slcm
from enums.final_state import FinalState
from paramiko.ssh_exception import NoValidConnectionsError


def connect_by_ssh(context, command, is_current_state):
    result = {}
    ssh = None
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh.connect(hostname=context.get('host'), username=context.get('user_name'),
                    password=context.get('password'), port=int(context.get('port')))
        transport = ssh.get_transport()
        session = transport.open_session()
        session.set_combine_stderr(True)
        session.get_pty()
        session.exec_command(command)
        stdin = session.makefile('wb', -1)
        stdout = session.makefile('rb', -1)
        stdin.write(context.get('password') + '\n')
        stdin.flush()
        if is_current_state:
            s_status = None
            for line in iter(stdout.readline, ''):
                s_status = line.rstrip()
            result['state'] = get_state_slcm(s_status.upper())
            if result['state'].upper() == FinalState.FAILED.value:
                result['code'] = -1
            else:
                result['code'] = stdout.channel.recv_exit_status()
        else:
            result['code'] = stdout.channel.recv_exit_status()
    except NoValidConnectionsError, e:
        ssh = None
        result = None
    finally:
        if ssh is not None:
            ssh.close()

    return result


def instance_ssh(context):
    ssh = None
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh.connect(hostname=context.get('host'), username=context.get('user_name'),
                    password=context.get('password'), port=int(context.get('port')))
    except NoValidConnectionsError, e:
        ssh = None
    finally:
        if ssh is not None:
            ssh.close()
    return ssh


def get_connect_instances(data):
    instance = None
    if data.get('context_type').lower() == 'ssh':
        context = data.get('context')
        instance = instance_ssh(context)
    return instance
