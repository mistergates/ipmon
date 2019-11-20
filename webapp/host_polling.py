import os
import sys
import platform
import subprocess
import socket
import time

from multiprocessing.pool import ThreadPool

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
from webapp import app, db
from webapp.database import Hosts

def poll_hosts():
    '''Polls hosts threaded and commits results to DB'''
    pool = ThreadPool(20)
    threads = []
    with app.app_context():
        hosts = Hosts.query.all()

        for host in hosts:
            # _poll_host_threaded(host)
            threads.append(pool.apply_async(_poll_host_threaded, (host,)))
        pool.close()
        pool.join()

        for thread in threads:
            thread.get()

        db.session.commit()


def _poll_host_threaded(host):
    status, poll_time, hostname = _poll_host(host.ip_address)
    host.status = status
    host.last_poll = poll_time
    host.hostname = hostname


def _poll_host(host):
    print('POLLING {}'.format(host))
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', host]
    response = subprocess.call(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    try:
        hostname = socket.getfqdn(host)
    except socket.error:
        hostname = 'Unknown'

    return ('Up' if response == 0 else 'Down', time.strftime('%Y-%m-%d %T'), hostname)
