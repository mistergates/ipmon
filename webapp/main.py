'''Main Web Application'''
import os
import sys
import time
import flask_login
import subprocess
import platform
import json

from multiprocessing.pool import ThreadPool
from flask import Blueprint, render_template, request, flash
from sqlalchemy import update

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
from webapp import db
from webapp.database import Hosts, HOSTS_SCHEMA

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
    return render_template('index.html', hosts=hosts, num_hosts=num_hosts, num_up=num_up, num_down=num_down)


@main.route('/pollHosts', methods=['GET'])
def poll_hosts():
    if request.method == 'GET':
        hosts = Hosts.query.all()
        for host in hosts:
            status, current_time = _poll_host(host.ip_address)
            update(Hosts).where(Hosts.id == host.id).values(
                status=status,
                last_poll=current_time
            )
        db.session.commit()
    return json.dumps(HOSTS_SCHEMA.dump(Hosts.query.all()))


@main.route('/addhosts', methods=['GET', 'POST'])
@flask_login.login_required
def add_hosts():
    '''Add Hosts Page'''
    if request.method == 'GET':
        return render_template('addHosts.html')
    elif request.method == 'POST':
        results = request.form.to_dict()

        status, current_time = _poll_host(results['ip'])

        # create new host database object
        new_host = Hosts(
            ip_address=results['ip'],
            hostname=results['hostname'],
            status=status,
            last_poll=current_time
        )

        try:
            # add the new host to the database
            db.session.add(new_host)
            db.session.commit()
            flash('Successfully added {}'.format(results['hostname']))
        except Exception as exc:
            flash('Failed to add {}: {}'.format(results['hostname'], exc))

        return render_template('addHosts.html')
        

#####################
# Private Functions #
#####################

def _poll_host(host):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', host]
    response = subprocess.call(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return ('Up' if response == 0 else 'Down', time.strftime('%Y-%m-%d %T'))


