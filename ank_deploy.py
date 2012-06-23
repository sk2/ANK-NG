
def package(src_dir, target):
        import tarfile
        import os
        tar_filename = "%s.tar.gz" % target
#time.strftime("%Y%m%d_%H%M", time.localtime())
        tar = tarfile.open(os.path.join(tar_filename), "w:gz")
        tar.add(src_dir)
        tar.close()
        return tar_filename


def transfer(host, username, local, remote):
    import paramiko
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(
        paramiko.AutoAddPolicy())
    ssh.connect(host, username = username)
    ftp = ssh.open_sftp()
    ftp.put(local, remote)
    ftp.close()

def extract(host, tar_file, cd_dir):
    from Exscript.protocols import SSH2
    from Exscript import Account

    def starting_host(protocol, index, data):
        print "Starting", data.group(index)

    def already_running(protocol, index, data):
        print "already_running", data.group(index)

    def data_received(data):
        print "data event", data

    #account = read_login()              
    account = Account("sknight")
    conn = SSH2()                       
    conn.connect(host)     
    conn.login(account)                 

#TODO: use a script template for this
    conn.add_monitor(r'Starting (\S+)', starting_host)
    conn.add_monitor(r'vstart: Virtual machine "(\S+)" is already running. Please', already_running)
    conn.data_received_event.connect(data_received)

    conn.execute('tar -xzf %s' % tar_file)
    print conn.response
    conn.execute('cd %s' % cd_dir)
    print conn.response
    conn.execute('pwd')
    print conn.response
    conn.execute('vlist')
    print conn.response
    print "Starting lab"
    conn.execute('lstart -p5 -o --con0=none')
    print conn.response
    conn.send("exit")

    conn.close() 

