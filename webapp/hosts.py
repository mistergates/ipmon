'''Hosts Module'''
import os
import sys
import flask_login
import json
import re

from flask import Blueprint, render_template, request, flash, redirect, url_for, send_from_directory

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
from webapp.database import Hosts, PollHistory, HostAlerts
from webapp import db, app
from webapp.api import get_web_themes, get_polling_config, get_active_theme, get_hosts
from webapp.polling import poll_host, update_poll_scheduler

hosts = Blueprint('hosts', __name__)


@hosts.route('/addHosts', methods=['GET', 'POST'])
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

            status, current_time, hostname = poll_host(ip_address, new_host=True)

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
        return redirect(url_for('hosts.add_hosts'))


@hosts.route('/updateHosts', methods=['GET', 'POST'])
@flask_login.login_required
def update_hosts():
    '''Update Hosts'''
    if request.method == 'GET':
        return render_template('updateHosts.html', hosts=json.loads(get_hosts()))
    elif request.method == 'POST':
        results = request.form.to_dict()
        host =  Hosts.query.filter_by(id=int(results['id'])).first()
        try:
            if results['hostname']:
                host.hostname = results['hostname']
            if results['ip_address']:
                host.ip_address = results['ip_address']
            db.session.commit()
            flash('Successfully updated host {}'.format(host.hostname), 'success')
        except Exception:
            flash('Failed to update host {}'.format(host.hostname), 'danger')

        return redirect(url_for('hosts.update_hosts'))


@hosts.route('/deleteHost', methods=['POST'])
@flask_login.login_required
def delete_host():
    '''Delete Hosts Page'''
    if request.method == 'POST':
        results = request.form.to_dict()
        host_id = int(results['id'])
        try:
            PollHistory.query.filter_by(host_id=host_id).delete()
            HostAlerts.query.filter_by(host_id=host_id).delete()
            Hosts.query.filter_by(id=host_id).delete()
            db.session.commit()
            flash('Successfully deleted {}'.format(results['hostname']), 'success')
        except Exception as exc:
            flash('Failed to delete {}: {}'.format(results['hostname'], exc), 'danger')

        return redirect(url_for('hosts.update_hosts'))