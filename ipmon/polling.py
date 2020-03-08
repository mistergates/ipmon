'''Host Polling Lib'''
import os
import sys
import platform
import subprocess
import socket
import time
import json

from multiprocessing.pool import ThreadPool
from datetime import date, timedelta

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
from ipmon import app, db, scheduler, log, config
from ipmon.database import Hosts, PollHistory, HostAlerts
from ipmon.api import get_all_hosts, get_host, get_polling_config, get_poll_history


def poll_host(host, new_host=False, count=3):
    '''Poll host via ICMP ping to see if it is up/down'''
    hostname = None

    if platform.system().lower() == 'windows':
        command = ['ping', '-n', str(count), '-w', '1000', host]
    else:
        command = ['ping', '-c', str(count), '-W', '1', host]

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
        scheduler.remove_job('Poll Hosts')
    except Exception:
        pass

    scheduler.add_job(id='Poll Hosts', func=_poll_hosts_threaded, trigger='interval', seconds=int(poll_interval), max_instances=1)


def add_poll_history_cleanup_cron():
    '''Adds crong job for poll history cleanup'''
    scheduler.add_job(id='Poll History Cleanup', func=_poll_history_cleanup_task, trigger='cron', hour='0', minute='30')


def get_hostname(ip_address):
    '''Gets the FQDN from an IP Address'''
    try:
        hostname = socket.getfqdn(ip_address)
    except socket.error:
        hostname = 'Unknown'

    return hostname


def _poll_hosts_threaded():
    log.debug('Starting host polling')
    s = time.perf_counter()

    with app.app_context():
        pool = ThreadPool(config['Max_Threads'])
        threads = []

        for host in json.loads(get_all_hosts()):
            threads.append(
                pool.apply_async(_poll_host_task, (host['id'],))
            )

        pool.close()
        pool.join()

        for thread in threads:
            host_info, new_poll_history, host_alert = thread.get()
            host = Hosts.query.filter_by(id=int(host_info['id'])).first()
            host.previous_status = host_info['previous_status']
            host.status = host_info['status']
            host.last_poll = host_info['last_poll']
            db.session.add(new_poll_history)
            if host_alert:
                db.session.add(host_alert)
        db.session.commit()

    log.debug("Host polling finished executing in {} seconds.".format(time.perf_counter() - s))


def _poll_host_task(host_id):
    with app.app_context():
        host_info = json.loads(get_host(int(host_id)))
        status, poll_time, hostname = poll_host(host_info['ip_address'])
        host_alert = None

        # Update host status
        host_info['previous_status'] = host_info['status']
        host_info['status'] = status
        host_info['last_poll'] = poll_time

        # Add poll history for host
        if hostname:
            host_info['hostname'] = hostname

        new_poll_history = PollHistory(
            host_id=host_info['id'],
            poll_time=poll_time,
            poll_status=status
        )

        log.info('{} - {}'.format(host_info['alerts_enabled'], type(host_info['alerts_enabled'])))
        if host_info['alerts_enabled'] and host_info['previous_status'] != status:
            # Create alert if status changed
            host_alert = HostAlerts(
                host_id=host_info['id'],
                hostname=host_info['hostname'],
                ip_address=host_info['ip_address'],
                host_status=host_info['status'],
                poll_time=host_info['last_poll']
            )

    return host_info, new_poll_history, host_alert


def _poll_history_cleanup_task():
    log.debug('Starting poll history cleanup')
    s = time.perf_counter()

    with app.app_context():
        retention_days = json.loads(get_polling_config())['history_truncate_days']
        current_date = date.today()

        # Delete poll history where date_created < today - retention_days
        PollHistory.query.filter(
            PollHistory.date_created < (current_date - timedelta(days=retention_days))
        ).delete()

        db.session.commit()

    log.debug("Poll history cleanup finished executing in {} seconds.".format(time.perf_counter() - s))
