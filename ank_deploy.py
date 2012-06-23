
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
    from Exscript import Account
    from Exscript.util.start import start
    from Exscript.protocols.Exception import InvalidCommandException

    def starting_host(protocol, index, data):
        print data.group(index)

    def lab_started(protocol, index, data):
        print "Lab started"


    #account = read_login()              
    """
    account = Account("sknight")
    conn = SSH2()                       
    conn.connect(host)     
    conn.login(account)                 

#TODO: use a script template for this
    conn.add_monitor(r'Starting (\S+)', starting_host)
    conn.add_monitor(r'vstart: Virtual machine ', already_running)
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
    """

    def do_something(thread, host, conn):
        conn.add_monitor(r'Starting (\S+)', starting_host)
        conn.add_monitor(r'The lab has been started', lab_started)
        #conn.data_received_event.connect(data_received)
        conn.execute('tar -xzf %s' % tar_file)
        conn.execute('cd %s' % cd_dir)
        conn.execute('vlist')
        print "Starting lab"
        start_command = 'lstart -p5 -o --con0=none'
        try:
            conn.execute(start_command)
        except InvalidCommandException, error:
            if "already running" in str(error):
                print "Already Running" #TODO: handle appropriately
                conn.execute("vclean -K")
                print "halted"
                conn.execute(start_command)
        conn.send("exit")


    accounts = [Account("sknight")]  # No account needed.
    hosts = ['ssh://%s' % host]
    start(accounts, hosts, do_something, verbose = 0)

