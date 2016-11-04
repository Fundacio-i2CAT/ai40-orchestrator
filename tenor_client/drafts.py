import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(
    paramiko.AutoAddPolicy())
ssh.connect('172.24.4.53', username='root', key_filename='keys/anella')
stdin, stdout, stderr = ssh.exec_command("uptime")

print stdout.readlines()

ssh.close()
