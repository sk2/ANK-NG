import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(
    paramiko.AutoAddPolicy())
ssh.connect('trc1.trc.adelaide.edu.au', username='sknight')
ftp = ssh.open_sftp()
ftp.put('nren.graphml', 'remotefile.py')
ftp.close()

