'''Hosts Module'''
import os
import sys
import flask_login
import json

from multiprocessing.pool import ThreadPool
from flask import Blueprint, render_template, request, flash, redirect, url_for

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
from ipmon.database import Hosts, PollHistory, HostAlerts
from ipmon import db, config, log
from ipmon.api import get_all_hosts
from ipmon.polling import poll_host
from ipmon.forms import AddHostsForm
from wtforms.validators import IPAddress

hosts = Blueprint('hosts', __name__)

######################
# Routes #############
######################
@hosts.route('/addHosts', methods=['GET', 'POST'])
@flask_login.login_required
def add_hosts():
    '''Add Hosts Page'''
    form = AddHostsForm()
    if request.method == 'GET':
        return render_template('addHosts.html', form=form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            pool = ThreadPool(config['Max_Threads'])
            threads = []
            for ip_address in form.ip_address.data.split('\n'):
                ip_address = ip_address.strip()
                validator = IPAddress(ipv4=True)

                if not validator.check_ipv4(ip_address):
                    flash('{} Is not a valid IP address'.format(ip_address), 'danger')
                    continue

                if Hosts.query.filter_by(ip_address=ip_address).first():
                    flash('IP Address {} already exists.'.format(ip_address), 'danger')
                    continue

                threads.append(
                    pool.apply_async(_add_hosts_threaded, (ip_address,))
                )

            pool.close()
            pool.join()
            for thread in threads:
                new_host = thread.get()
                try:
                    # add the new host to the database
                    db.session.add(new_host)
                    flash(u'Successfully added {} ({})'.format(new_host.ip_address, new_host.hostname), 'success')
                except Exception as exc:
                    flash(u'Failed to add {}'.format(new_host.ip_address), 'danger')
                    log.error('Failed to add {} to database. Exception: {}'.format(new_host, exc))
                    continue

            db.session.commit()
        else:
            for dummy, errors in form.errors.items():
                for error in errors:
                    flash(error, 'danger')

        return redirect(url_for('hosts.add_hosts'))


@hosts.route('/updateHosts', methods=['GET', 'POST'])
@flask_login.login_required
def update_hosts():
    '''Update Hosts'''
    if request.method == 'GET':
        return render_template('updateHosts.html', hosts=json.loads(get_all_hosts()))
    elif request.method == 'POST':
        results = request.form.to_dict()
        host =  Hosts.query.filter_by(id=int(results['id'])).first()
        try:
            if results['hostname']:
                host.hostname = results['hostname']
            if results['ip_address']:
                host.ip_address = results['ip_address']
            if results['alerts'] != str(host.alerts_enabled):
                host.alerts_enabled = False if results['alerts'] == 'False' else True
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


######################
# Private Functions ##
######################
def _add_hosts_threaded(ip_address):
    status, current_time, hostname = poll_host(ip_address, new_host=True)

    # create new host database object
    new_host = Hosts(
        ip_address=ip_address,
        hostname=hostname,
        status=status,
        last_poll=current_time
    )

    return new_host