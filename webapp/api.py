'''API Module'''
import os
import sys
import flask_login
import json

from flask import Blueprint

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
from webapp.database import Hosts, Polling, PollHistory, WebThemes, Users, SmtpServer, HostAlerts, Schemas

api = Blueprint('api', __name__)

#####################
# API Routes ########
#####################
@api.route('/getHosts', methods=['GET'])
def get_hosts():
    '''Get all hosts'''
    return json.dumps(Schemas.HOSTS_SCHEMA.dump(Hosts.query.all()))


@api.route('/getHosts/<id>', methods=['GET'])
def get_host(_id):
    '''Get host by ID'''
    return json.dumps(Schemas.HOST_SCHEMA.dump(Hosts.query.filter_by(id=_id).first()))


@api.route('/getHostAlerts', methods=['GET'])
def get_all_host_alerts():
    '''Get new host alerts'''
    return json.dumps(Schemas.HOST_ALERTS_SCHEMA.dump(HostAlerts.query.join(Hosts).all()))


@api.route('/getNewHostAlerts', methods=['GET'])
def get_new_host_alerts():
    '''Get new host alerts'''
    return json.dumps(Schemas.HOST_ALERTS_SCHEMA.dump(HostAlerts.query.filter_by(alert_cleared=False)))


@api.route('/getPollingConfig', methods=['GET'])
def get_polling_config():
    '''Get polling config'''
    return json.dumps(Schemas.POLLING_SCHEMA.dump(Polling.query.filter_by(id=1).first()))


@api.route('/getPollHistory/<host_id>', methods=['GET'])
def get_poll_history(host_id):
    '''Get poll history for a single host'''
    return json.dumps(Schemas.POLL_HISTORY_SCHEMA.dump(PollHistory.query.filter_by(host_id=host_id)))


@api.route('/getAlertsEnabled', methods=['GET'])
def get_alerts_enabled():
    '''Get whether alerts are enabled or not'''
    status = Schemas.USER_SCHEMA.dump(Users.query.first())['alerts_enabled']
    return json.dumps({'alerts_enabled': status})


@api.route('/getSmtpConfigured', methods=['GET'])
def get_smtp_configured():
    '''Get whether SMTP configured or not'''
    if Schemas.SMTP_SCHEMA.dump(SmtpServer.query.first()):
        return json.dumps({'smtp_configured': True})
    
    return json.dumps({'smtp_configured': False})


@api.route('/getWebThemes', methods=['GET'])
def get_web_themes():
    '''Get all web themese'''

    return json.dumps(Schemas.WEB_THEMES_SCHEMA.dump(WebThemes.query.all()))


@api.route('/getActiveTheme', methods=['GET'])
def get_active_theme():
    '''Get active theme'''
    return json.dumps(Schemas.WEB_THEME_SCHEMA.dump(WebThemes.query.filter_by(active=True).first()))


@api.route('/getHostCounts', methods=['GET'])
def get_host_counts():
    '''Get host total, available, unavailable host counts'''
    total = Hosts.query.count()
    num_up = Hosts.query.filter(Hosts.status == 'Up').count()
    num_down = Hosts.query.filter(Hosts.status == 'Down').count()

    return json.dumps({'total_hosts': total, 'available_hosts': num_up, 'unavailable_hosts': num_down})
