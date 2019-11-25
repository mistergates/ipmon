'''Host Polling Lib'''
import os
import sys
import platform
import subprocess
import socket
import time

from multiprocessing.pool import ThreadPool

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
from webapp import app, db, scheduler, config
from webapp.database import Hosts, PollHistory, HostAlerts

def poll_hosts():
    '''Polls hosts threaded and commits results to DB'''
    pool = ThreadPool(config['Pool_Size'])
    threads = []
    with app.app_context():
        hosts = Hosts.query.all()

        for host in hosts:
            threads.append(pool.apply_async(_poll_host_threaded, (host,)))
        pool.close()
        pool.join()

        for thread in threads:
            poll_history, host_alert = thread.get()
            db.session.add(poll_history)
            if host_alert:
                db.session.add(host_alert)
            db.session.commit()


def _poll_host_threaded(host):
    status, poll_time, hostname = poll_host(host.ip_address)

    # Update host status
    host.previous_status = host.status
    host.status = status
    host.last_poll = poll_time

    # Add poll history for host
    with app.app_context():
        if hostname:
            host.hostname = hostname

        new_poll_history = PollHistory(
            host_id=host.id,
            poll_time=poll_time,
            poll_status=status
        )
        # db.session.add(new_poll_history)

        # Create alert if status changed
        new_host_alert = None
        if host.previous_status != status:
            new_host_alert = HostAlerts(
                host_id=host.id,
                hostname=host.hostname,
                ip_address=host.ip_address,
                host_status=host.status,
                poll_time=host.last_poll
            )
            # db.session.add(new_host_alert)

        return new_poll_history, new_host_alert
        # db.session.commit()


def poll_host(host, new_host=False, count=1):
    '''Poll host via ICMP ping to see if it is up/down'''
    hostname = None

    if platform.system().lower() == 'windows':
        command = ['ping', '-n', str(count), '-w', '500', host]
    else:
        command = ['ping', '-c', str(count), host]

    response = subprocess.call(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    if new_host:
        hostname = get_hostname(host)

    return ('Up' if response == 0 else 'Down', time.strftime('%Y-%m-%d %T'), hostname)


def update_poll_scheduler(poll_interval):
    '''Updates the Poll Hosts schedula via APScheduler'''
    # Attempt to remove the current scheduler
    try:
        scheduler.scheduler.remove_job('Poll Hosts')
    except Exception:
        pass

    scheduler.scheduler.add_job(id='Poll Hosts', func=poll_hosts, trigger='interval', seconds=int(poll_interval), max_instances=1)


def get_hostname(ip_address):
    try:
        hostname = socket.getfqdn(ip_address)
    except socket.error:
        hostname = 'Unknown'

    return hostname