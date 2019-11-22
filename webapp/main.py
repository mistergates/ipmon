'''Main Web Application'''
import os
import sys
import flask_login
import json
import re

from flask import Blueprint, render_template, request, flash, redirect, url_for, send_from_directory

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
from webapp.database import Hosts, Polling, PollHistory, WebThemes
from webapp.database import HOSTS_SCHEMA, POLLING_SCHEMA, POLL_HISTORY_SCHEMA, WEB_THEMES_SCHEMA, WEB_THEME_SCHEMA
from webapp import db, app
from webapp.host_polling import poll_host, update_poll_scheduler

main = Blueprint('main', __name__)

#####################
# App Routes ########
#####################
@main.route('/')
def index():
    '''Index page'''
    interval = int(json.loads(get_polling_config())['poll_interval']) * 1000
    return render_template('index.html', poll_interval=interval)


@main.route('/favicon.ico')
def favicon():
    '''Favicon'''
    return send_from_directory(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@main.route('/getHostCounts', methods=['GET'])
def get_host_counts():
    total = Hosts.query.count()
    num_up = Hosts.query.filter(Hosts.status == 'Up').count()
    num_down = Hosts.query.filter(Hosts.status == 'Down').count()

    return json.dumps({'total_hosts': total, 'available_hosts': num_up, 'unavailable_hosts': num_down})


@main.route('/setTheme', methods=['GET', 'POST'])
@flask_login.login_required
def set_theme():
    '''Set Theme'''
    if request.method == 'GET':
        return render_template('setTheme.html', themes=get_web_themes())
    elif request.method == 'POST':
        results = request.form.to_dict()
        print(results)

        try:
            for theme in get_web_themes():
                print(theme)
                theme_obj = WebThemes.query.filter_by(id=int(theme['id'])).first()
                if theme_obj.id == int(results['id']):
                    theme_obj.active = True
                else:
                    theme_obj.active = False
            db.session.commit()
            flash('Successfully updated theme', 'success')
        except Exception as exc:
            flash('Failed to update theme: {}'.format(exc), 'danger')
    return redirect(url_for('main.set_theme'))


@main.route('/configurePolling', methods=['GET', 'POST'])
@flask_login.login_required
def configure_polling():
    '''Poll Interval'''
    if request.method == 'GET':
        polling_config = POLLING_SCHEMA.dump(Polling.query.filter_by(id=1).first())
        return render_template('pollingConfig.html', polling_config=polling_config)
    elif request.method == 'POST':
        results = request.form.to_dict()

        polling_config = Polling.query.filter_by(id=1).first()
        try:
            if results['polling_interval']:
                polling_config.poll_interval = int(results['polling_interval'])
            if results['history_truncate_days']:
                polling_config.history_truncate_days = int(results['history_truncate_days'])
            db.session.commit()
        except Exception:
            flash('Failed to update polling interval', 'danger')
            return redirect(url_for('main.configure_polling'))

        # Update scheduled polling interval
        if results['polling_interval']:
            update_poll_scheduler(results['polling_interval'])

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
        return redirect(url_for('main.add_hosts'))


@main.route('/updateHosts', methods=['GET', 'POST'])
@flask_login.login_required
def update_hosts():
    '''Update Hosts'''
    if request.method == 'GET':
        return render_template('updateHosts.html', hosts=HOSTS_SCHEMA.dump(Hosts.query.all()))
    elif request.method == 'POST':
        results = request.form.to_dict()

        host =  Hosts.query.filter_by(id=int(results['id'])).first()
        try:
            if results['hostname']:
                print('Updating hostname')
                host.hostname = results['hostname']
            if results['ip_address']:
                print('Updating IP')
                host.ip_address = results['ip_address']
            db.session.commit()
            flash('Successfully updated host', 'success')
        except Exception:
            flash('Failed to update host', 'danger')

        return redirect(url_for('main.update_hosts'))


@main.route('/deleteHost', methods=['POST'])
@flask_login.login_required
def delete_host():
    '''Delete Hosts Page'''
    if request.method == 'POST':
        results = request.form.to_dict()

        try:
            Hosts.query.filter_by(id=results['id']).delete()
            PollHistory.query.filter_by(host_id=results['id']).delete()
            db.session.commit()
            flash('Successfully deleted {}'.format(results['hostname']), 'success')
        except Exception as exc:
            flash('Failed to delete {}: {}'.format(results['hostname'], exc), 'danger')

        return redirect(url_for('main.update_hosts'))


#####################
# API Routes ########
#####################
@main.route('/getHosts', methods=['GET'])
def get_hosts():
    return json.dumps(HOSTS_SCHEMA.dump(Hosts.query.all()))


@main.route('/getPollingConfig', methods=['GET'])
def get_polling_config():
    return json.dumps(POLLING_SCHEMA.dump(Polling.query.filter_by(id=1).first()))


@main.route('/getPollHistory/<host_id>', methods=['GET'])
def get_poll_history(host_id):
    return json.dumps(POLL_HISTORY_SCHEMA.dump(PollHistory.query.filter_by(host_id=host_id)))


@main.route('/getWebThemes', methods=['GET'])
def get_web_themes():
    return WEB_THEMES_SCHEMA.dump(WebThemes.query.all())


##########################
# Custom Jinja Functions #
##########################
def get_active_theme_path():
    return WEB_THEME_SCHEMA.dump(WebThemes.query.filter_by(active=True).first())['theme_path']
app.add_template_global(get_active_theme_path, name='get_active_theme_path')
