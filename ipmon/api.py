'''API Module'''
import os
import sys
import flask_login
import json

from flask import Blueprint

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
from ipmon import db
from ipmon.database import Hosts, Polling, PollHistory, WebThemes, Users, SmtpServer, HostAlerts
from ipmon.schemas import Schemas

api = Blueprint('api', __name__)

#####################
# API Routes ########
#####################
@api.route('/hosts', methods=['GET'])
def get_all_hosts():
    '''Get all hosts'''
    return json.dumps(Schemas.hosts(many=True).dump(Hosts.query.all()))


@api.route('/hosts/<id>', methods=['GET'])
def get_host(_id):
    '''Get host by ID'''
    return json.dumps(Schemas.hosts(many=False).dump(Hosts.query.filter_by(id=_id).first()))


@api.route('/hostsDataTable', methods=['GET'])
def get_all_hosts_datatable():
    '''Get all hosts'''
    data = {
        "columns": [
            { "data": "hostname", "title": "Hostname" },
            { "data": "ip_address", "title": "IP Address" },
            { "data": "last_poll", "title": "Last Poll" },
            { "data": "status", "title": "Status" }
        ],
        "data": Schemas.hosts(many=True).dump(Hosts.query.all())
    }
    return json.dumps(data)

@api.route('/hostAlerts', methods=['GET'])
def get_all_host_alerts():
    '''Get all host alerts'''
    return json.dumps(Schemas.host_alerts(many=True).dump(HostAlerts.query.join(Hosts).all()))


@api.route('/hostAlerts/new', methods=['GET'])
def get_new_host_alerts():
    '''Get new host alerts'''
    return json.dumps(Schemas.host_alerts(many=True).dump(HostAlerts.query.filter_by(alert_cleared=False)))


@api.route('/pollingConfig', methods=['GET'])
def get_polling_config():
    '''Get polling config'''
    return json.dumps(Schemas.polling_config().dump(Polling.query.filter_by(id=1).first()))


@api.route('/pollHistory/<host_id>', methods=['GET'])
def get_poll_history(host_id):
    '''Get poll history for a single host'''
    return json.dumps(Schemas.poll_history(many=True).dump(PollHistory.query.filter_by(host_id=host_id)))

# TODO Should check this by user id
@api.route('/alertsEnabled', methods=['GET'])
def get_alerts_enabled():
    '''Get whether alerts are enabled or not'''
    status = Schemas.users(many=False).dump(Users.query.first())['alerts_enabled']
    return json.dumps({'alerts_enabled': status})


@api.route('/smtpConfigured', methods=['GET'])
def get_smtp_configured():
    '''Get whether SMTP configured or not'''
    config = json.loads(get_smtp_config())
    if config['smtp_server'] and config['smtp_port'] and config['smtp_sender']:
        return json.dumps({'smtp_configured': True})
    return json.dumps({'smtp_configured': False})


@api.route('/smtpConfig', methods=['GET'])
def get_smtp_config():
    '''Get SMTP config'''
    return json.dumps(Schemas.smtp_config().dump(SmtpServer.query.first()))


@api.route('/webThemes', methods=['GET'])
def get_web_themes():
    '''Get all web themese'''
    return json.dumps(Schemas.web_themes(many=True).dump(WebThemes.query.all()))


@api.route('/webThemes/active', methods=['GET'])
def get_active_theme():
    '''Get active theme'''
    return json.dumps(Schemas.web_themes(many=False).dump(WebThemes.query.filter_by(active=True).first()))


@api.route('/hostCounts', methods=['GET'])
def get_host_counts():
    '''Get host total, available, unavailable host counts'''
    total = Hosts.query.count()
    num_up = Hosts.query.filter(Hosts.status == 'Up').count()
    num_down = Hosts.query.filter(Hosts.status == 'Down').count()

    return json.dumps({'total_hosts': total, 'available_hosts': num_up, 'unavailable_hosts': num_down})


@api.route('/hosts/all', methods=['DELETE'])
def delete_all_hosts():
    '''Deletes all hosts'''
    Hosts.query.delete()
    HostAlerts.query.delete()
    PollHistory.query.delete()

    db.session.commit()

    return json.dumps({'status': 'success'})
