import os
import sys
import platform
import subprocess
import socket
import time

from multiprocessing.pool import ThreadPool

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
from webapp import app, db, scheduler
from webapp.database import Hosts, PollHistory

def poll_hosts():
    '''Polls hosts threaded and commits results to DB'''
    pool = ThreadPool(20)
    threads = []
    with app.app_context():
        hosts = Hosts.query.all()

        for host in hosts:
            threads.append(pool.apply_async(_poll_host_threaded, (host,)))
        pool.close()
        pool.join()

        for thread in threads:
            thread.get()

        db.session.commit()


def _poll_host_threaded(host):
    status, poll_time, hostname = poll_host(host.ip_address)

    # Update host status
    host.status = status
    host.last_poll = poll_time
    host.hostname = hostname

    # Add poll history for host
    with app.app_context():
        new_poll_history = PollHistory(
            host_id=host.id,
            poll_time=poll_time,
            poll_status=status
        )
        db.session.add(new_poll_history)
        db.session.commit()


def poll_host(host):
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


def update_poll_scheduler(poll_interval):
    scheduler.scheduler.remove_all_jobs()
    scheduler.scheduler.add_job(id='Poll Hosts', func=poll_hosts, trigger='interval', seconds=poll_interval, max_instances=1)
