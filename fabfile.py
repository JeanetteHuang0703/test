from __future__ import with_statement
from fabric.api import *
from fabric.operations import put, get
from fabric.contrib.console import confirm
from fabric.contrib.files import append
import time, sys, os
import scanf
from io import BytesIO
import math

your_git_username = ""
your_git_password = ""


@parallel
def host_type():
    run('uname -s')


@parallel
def gettime():
    run('date +%s.%N')


@parallel
def checkLatency():
    '''
    PING 52.49.163.101 (52.49.163.101) 56(84) bytes of data.
    64 bytes from 52.49.163.101: icmp_seq=1 ttl=45 time=141 ms

    --- 52.49.163.101 ping statistics ---
    1 packets transmitted, 1 received, 0% packet loss, time 0ms
    rtt min/avg/max/mdev = 141.722/141.722/141.722/0.000 ms
    '''
    resDict = []
    totLen = len(env.hosts)
    for destination in env.hosts:
        waste = BytesIO()
        with hide('output', 'running'):
            res = run('ping -c 3 %s' % destination, stdout=waste, stderr=waste).strip().split('\n')[1].strip()
        lat = scanf.sscanf(res, '%d bytes from %s icmp_seq=%d ttl=%d time=%f ms')[-1]
        resDict.append(lat)
    print
    ' '.join([env.host_string, str(sorted(resDict)[int(math.ceil(totLen * 0.75))]), str(sum(resDict) / len(resDict))])


@parallel
def ping():
    run('ping -c 5 google.com')
    run('echo "synced transactions set"')
    run('ping -c 100 google.com')


@parallel
def cloneRepo():
    run('git clone https://sduan:PASSWORD@bitbucket.org/sduan/beat-bft.git')


@parallel
def addhoc():
    run('sudo lsof -t -i tcp:49500 | xargs kill -9')


def checkfile():
    with cd('~/BEAT/BEAT0/'):
        run('ls')


@parallel
def install_dependencies_addhoc():
    sudo('pip install greenlet --upgrade')
    sudo('pip install gevent')


@parallel
def install_dependencies():
    sudo('apt-get update')
    sudo('apt-get -y install git')
    sudo('apt-get -y install python3-pip')
    sudo('pip3 install pycrypto')
    sudo('apt-get -y install flex')
    sudo('apt-get -y install bison')
    sudo('apt-get -y install libgmp-dev')
    sudo('apt-get -y install libssl-dev')
    sudo('pip3 install pycryptodome')
    sudo('pip3 install gevent')
    sudo('pip3 install gipc')
    sudo('pip3 install zfec')


@parallel
def installPBCandCharm():
    # with cd('~/adaptive/thresholdSig'):
    # run('sudo rm -r *.keys *.key')
    # sudo('apt-get -y install make')
    run('wget https://crypto.stanford.edu/pbc/files/pbc-0.5.14.tar.gz')
    run('tar -xvf pbc-0.5.14.tar.gz')
    with cd('pbc-0.5.14'):
        run('./configure')
        run('make')
        sudo('make install')
    # sudo('pip install --upgrade setuptools')
    # sudo('sudo -H pip2 install --upgrade pip')
    # Charm install
    with settings(warn_only=True):
        if run('test -d charm').failed:
            run('git clone https://github.com/JHUISI/charm.git')
    with cd('charm'):
        run('git checkout dev')
        run('./configure.sh')
        sudo('make install')


@parallel
def prepare():
    syncKeys()
    install_dependencies()
    cloneRepo()
    git_pull()


@parallel
def stopProtocols():
    with settings(warn_only=True):
        run('killall python')
        run('killall dtach')
        run('killall server.py')


@parallel
def removeHosts():
    run('rm ~/hosts')


@parallel
def writeHosts():
    put('./hosts', '~/')


@parallel
def kill_All():
    run('killall -9 server')
    run('killall -9 client')
    #run('lsof -t -i tcp:49500 | xargs kill -9')
    # run('killall python')
    # run('kill httpd')
    # run('pgrep command | xargs kill')


@parallel
def kill_Server():
    run('killall -9 server')



@parallel
def set_ulimit():
    #run('ulimit -n 4096')
    run('ulimit -a')


# @parallel
# def fetchLogs():
#     get('~/msglog.TorMultiple',
#         'logs/%(host)s' + time.strftime('%Y-%m-%d_%H:%M:%SZ', time.gmtime()) + '.log')

@parallel
def checkLog():
    with cd('~/var/log/'):
        run('ls')

@parallel
def clearLog():
    run('rm -R ~/var')

@parallel
def fetchLogs():
    #run('sudo chmod -R 777 ~/var/log')
    get('~/var/log/*', 'var/log/')


@parallel
def fetchLimit():
    #run('sudo chmod -R 777 ~/var/log')
    get('/etc/security/limits.conf', 'etc/')


@parallel
def fetchEvaLogs(ID_):
    sid = int(ID_)
    #run('sudo chmod -R 777 ~/var/log')
    get('~/var/log/%d/*Eva.log' % sid, 'var/log/' + ID_ + '/' + time.strftime("%Y%m%d", time.localtime()) + '_Eva.log')


@parallel
def syncKeys():
    with settings(warn_only=True):
        with cd('~/etc'):
            if run('test -d thresprf_key').failed:
                run('mkdir thresprf_key')
    put('./etc/thresprf_key/*', '~/etc/thresprf_key/')


@parallel
def syncConf():
    with settings(warn_only=True):
        try:
            run('rm -R ~/etc')
        except:
            pass
    run('mkdir ~/etc')
    put('./etc/*', '~/etc/')


@parallel
def syncJsonOnly():
    with settings(warn_only=True):
        if run('test -d etc').failed:
            run('mkdir ~/etc')
        put('./etc/*.json', '~/etc/')


@parallel
def syncExcute():
    try:
        run('rm -R ~/excute')
    except:
        pass
    try:
        run('mkdir ~/excute')
    except :
        pass
    put('./server', '~/excute')
    put('./client', '~/excute')
    run('chmod 777 ~/excute/client')
    run('chmod 777 ~/excute/server')


@parallel
def syncLimit():
    run('sudo chmod 777 /etc/security/limits.conf')
    put('./etc/limits.conf', '/etc/security/')


@parallel
def runClient(id_, type_, number_, msg='hello', frequence=0):
    print(id_, type_, number_, msg, frequence)
    run('./excute/client %s %s %s %s %s' % (id_, type_, number_, msg, frequence))

import socketserver, time

start_time = 0
sync_counter = 0
N = 1
t = 1


class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.rfile.readline().strip()
        print
        "%s finishes at %lf" % (self.client_address[0], time.time() - start_time)
        print
        self.data
        sync_counter += 1
        if sync_counter >= N - t:
            print
            "finished at %lf" % (time.time() - start_time)


# def runServer():  # deprecated
#     global start_time, sync_counter, N, t
#     N = int(Nstr)
#     t = int(tstr)
#     start_time = time.time()
#     sync_counter = 0
#     server = socketserver.TCPServer(('0.0.0.0', 51234), MyTCPHandler)
#     server.serve_forever()


@parallel
def runServer(ID_):
    sid = int(ID_)
    run('./excute/server %d' % sid)


# @parallel
# def runServer():
#     with shell_env(LIBRARY_PATH='/usr/local/lib', LD_LIBRARY_PATH='/usr/local/lib'):
#         run('./excute/server 0')


@parallel
def checkServerState():
    run('ps -ef | grep server')

@parallel
def runProtocol_local(N_, t_, B_):
    N = int(N_)
    t = int(t_)
    B = int(B_) * N
    with shell_env(LIBRARY_PATH='/usr/local/lib', LD_LIBRARY_PATH='/usr/local/lib'):
        with cd('~/BEAT/BEAT0'):
            run('python -m BEAT.test.honest_party_test -k'
                ' thsig%d_%d.keys -e ecdsa%d.keys -b %d -n %d -t %d -c thenc%d_%d.keys' % (N, t, t, B, N, t, N, t))


@parallel
def runProtocol(N_, t_, B_, timespan_, tx='tx'):
    N = int(N_)
    t = int(t_)
    B = int(B_) * N  # now we don't have to calculate them anymore
    timespan = int(timespan_)
    print
    N, t, B, timespan
    with shell_env(LIBRARY_PATH='/usr/local/lib', LD_LIBRARY_PATH='/usr/local/lib'):
        with cd('~/beat/BEAT0'):
            run('python -m BEAT.test.honest_party_test_EC2 -k'
                ' thsig%d_%d.keys -e ecdsa%d.keys -a %d -b %d -n %d -t %d -c thenc%d_%d.keys' % (
                N, t, t, timespan, B, N, t, N, t))


@parallel
def git_pull():
    with settings(warn_only=True):
        if run('test -d beat').failed:
            run('git clone https://%s:%s@github.com/fififish/beat.git' % (your_git_username, your_git_password))
    with cd('~/beat/'):
        run('git reset --hard origin/master')
        run('git clean -fxd')
        run('git pull')

