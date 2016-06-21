import paramiko
from common.utils import get_state


def connect_by_ssh(context, command, is_current_state):
    ssh = None
    result = {}
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
            result['code'] = stdout.channel.recv_exit_status()
            result['state'] = get_state(s_status.upper())
        else:
            result['code'] = stdout.channel.recv_exit_status()
    finally:
        if ssh is not None:
            ssh.close()

    return result
