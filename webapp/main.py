'''Main Web Application'''
import os
import sys
import time
import flask_login
import subprocess
import platform
import json
import socket
import re

from werkzeug.exceptions import HTTPException
from multiprocessing.pool import ThreadPool
from flask import Blueprint, render_template, request, flash, redirect, url_for

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
from webapp.database import Hosts, Polling, HOSTS_SCHEMA, POLLING_SCHEMA
from webapp import db


main = Blueprint('main', __name__)

#####################
# App Routes ########
#####################
@main.route('/')
def index():
    '''Index page'''
    num_hosts = Hosts.query.count()
    num_up = Hosts.query.filter(Hosts.status == 'Up').count()
    num_down = Hosts.query.filter(Hosts.status == 'Down').count()
    hosts = HOSTS_SCHEMA.dump(Hosts.query.all())
    poll_interval = int(POLLING_SCHEMA.dump(Polling.query.filter_by(id=1).first())['poll_interval']) * 1000
    return render_template('index.html', hosts=hosts, num_hosts=num_hosts, num_up=num_up, num_down=num_down, poll_interval=poll_interval)


@main.route('/pollHosts', methods=['GET'])
def poll_hosts():
    '''Polls hosts threaded and commits results to DB'''
    if request.method == 'GET':
        pool = ThreadPool(20)
        threads = []
        hosts = Hosts.query.all()
        for host in hosts:
            threads.append(pool.apply_async(_poll_host_threaded, (host,)))
        pool.close()
        pool.join()

        for thread in threads:
            thread.get()

        db.session.commit()
    return json.dumps(HOSTS_SCHEMA.dump(Hosts.query.all()))


@main.route('/pollInterval', methods=['GET', 'POST'])
@flask_login.login_required
def poll_interval():
    '''Poll Interval'''
    if request.method == 'GET':
        poll_interval = POLLING_SCHEMA.dump(Polling.query.filter_by(id=1).first())['poll_interval']
        return render_template('pollingInterval.html', poll_interval=poll_interval)
    elif request.method == 'POST':
        results = request.form.to_dict()

        try:
            polling_interval = int(results['polling_interval'])
        except ValueError:
            flash('Must provide an integer!', 'danger')
            return redirect(url_for('main.poll_interval'))

        polling_config = Polling.query.filter_by(id=1).first()
        try:
            polling_config.poll_interval = polling_interval
        except Exception:
            flash('Failed to update polling interval', 'danger')
            return redirect(url_for('main.poll_interval'))

        db.session.commit()
        flash('Successfully updated polling interval', 'success')
        return redirect(url_for('main.poll_interval'))


@main.route('/addHosts', methods=['GET', 'POST'])
@flask_login.login_required
def add_hosts():
    '''Add Hosts Page'''
    if request.method == 'GET':
        return render_template('addHosts.html')
    elif request.method == 'POST':
        results = request.form.to_dict()

        for ip_address in results['ip'].split('\n'):
            ip_address = ip_address.strip()

            regex = '''^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(
                        25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(
                        25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(
                        25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)'''

            if not re.search(regex, ip_address):
                flash('{} Is not a valid IP address'.format(ip_address), 'danger')
                continue

            if Hosts.query.filter_by(ip_address=ip_address).first():
                flash('IP Address {} already exists.'.format(ip_address), 'danger')
                continue

            status, current_time, hostname = _poll_host(ip_address)

            # create new host database object
            new_host = Hosts(
                ip_address=ip_address,
                hostname=hostname,
                status=status,
                last_poll=current_time
            )

            try:
                # add the new host to the database
                db.session.add(new_host)
                flash(u'Successfully added {} ({})'.format(ip_address, hostname), 'success')
            except Exception:
                flash(u'Failed to add {}'.format(hostname), 'danger')
                continue

        db.session.commit()
        return redirect(url_for('main.add_hosts'))


@main.route('/deleteHosts', methods=['GET', 'POST'])
@flask_login.login_required
def delete_hosts():
    '''Delete Hosts Page'''
    if request.method == 'GET':
        return render_template('deleteHosts.html', hosts=HOSTS_SCHEMA.dump(Hosts.query.all()))
    elif request.method == 'POST':
        results = request.form.to_dict()
        for host in results:
            host_id, hostname = host.split()
            try:
                Hosts.query.filter_by(id=host_id).delete()
                flash('Successfully deleted {}'.format(hostname), 'success')
            except Exception as exc:
                flash('Failed to delete {}: {}'.format(hostname, exc), 'danger')
                continue

        db.session.commit()
        return redirect(url_for('main.delete_hosts'))

#####################
# Private Functions #
#####################
def _poll_host_threaded(host):
    status, poll_time, hostname = _poll_host(host.ip_address)
    host.status = status
    host.last_poll = poll_time
    host.hostname = hostname


def _poll_host(host):
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
