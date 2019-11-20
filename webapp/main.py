'''Main Web Application'''
import os
import sys
import flask_login
import json
import re

from flask import Blueprint, render_template, request, flash, redirect, url_for

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
from webapp.database import Hosts, Polling, PollHistory
from webapp.database import HOSTS_SCHEMA, POLLING_SCHEMA, POLL_HISTORY_SCHEMA
from webapp import db, scheduler
from webapp.host_polling import poll_host, update_poll_scheduler

main = Blueprint('main', __name__)

#####################
# App Routes ########
#####################
@main.route('/')
def index():
    '''Index page'''
    interval = int(json.loads(get_polling_interval())['poll_interval']) * 1000
    return render_template('index.html', poll_interval=interval)


@main.route('/getHosts', methods=['GET'])
def get_hosts():
    return json.dumps(HOSTS_SCHEMA.dump(Hosts.query.all()))


@main.route('/getPollingInterval', methods=['GET'])
def get_polling_interval():
    return json.dumps(POLLING_SCHEMA.dump(Polling.query.filter_by(id=1).first()))


@main.route('/getPollHistory/<host_id>', methods=['GET'])
def get_poll_history(host_id):
    return json.dumps(POLL_HISTORY_SCHEMA.dump(PollHistory.query.filter_by(host_id=host_id)))


@main.route('/getHostCounts', methods=['GET'])
def get_host_counts():
    total = Hosts.query.count()
    num_up = Hosts.query.filter(Hosts.status == 'Up').count()
    num_down = Hosts.query.filter(Hosts.status == 'Down').count()

    return json.dumps({'total_hosts': total, 'available_hosts': num_up, 'unavailable_hosts': num_down})


@main.route('/configurePolling', methods=['GET', 'POST'])
@flask_login.login_required
def configure_polling():
    '''Poll Interval'''
    if request.method == 'GET':
        interval = POLLING_SCHEMA.dump(Polling.query.filter_by(id=1).first())['poll_interval']
        return render_template('pollingInterval.html', poll_interval=interval)
    elif request.method == 'POST':
        results = request.form.to_dict()

        try:
            polling_interval = int(results['polling_interval'])
        except ValueError:
            flash('Must provide an integer!', 'danger')
            return redirect(url_for('main.configure_polling'))

        polling_config = Polling.query.filter_by(id=1).first()
        try:
            polling_config.poll_interval = polling_interval
        except Exception:
            flash('Failed to update polling interval', 'danger')
            return redirect(url_for('main.configure_polling'))

        db.session.commit()

        # Update scheduled polling interval
        update_poll_scheduler(polling_interval)

        flash('Successfully updated polling interval', 'success')
        return redirect(url_for('main.configure_polling'))


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

            status, current_time, hostname = poll_host(ip_address)

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
