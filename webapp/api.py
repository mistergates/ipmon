'''API Module'''
import os
import sys
import flask_login
import json

from flask import Blueprint

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
from webapp.database import Hosts, Polling, PollHistory, WebThemes, Users, SmtpServer, HostAlerts
from webapp.database import HOSTS_SCHEMA, POLLING_SCHEMA, POLL_HISTORY_SCHEMA, WEB_THEMES_SCHEMA, WEB_THEME_SCHEMA, USER_SCHEMA, SMTP_SCHEMA, HOST_ALERTS_SCHEMA

api = Blueprint('api', __name__)

#####################
# API Routes ########
#####################
@api.route('/getHosts', methods=['GET'])
def get_hosts():
    '''Get all hosts'''
    return json.dumps(HOSTS_SCHEMA.dump(Hosts.query.all()))


@api.route('/getHostAlerts', methods=['GET'])
def get_all_host_alerts():
    '''Get new host alerts'''
    return json.dumps(HOST_ALERTS_SCHEMA.dump(HostAlerts.query.join(Hosts).all()))


@api.route('/getNewHostAlerts', methods=['GET'])
def get_new_host_alerts():
    '''Get new host alerts'''
    return json.dumps(HOST_ALERTS_SCHEMA.dump(HostAlerts.query.filter_by(alert_cleared=False)))


@api.route('/getPollingConfig', methods=['GET'])
def get_polling_config():
    '''Get polling config'''
    return json.dumps(POLLING_SCHEMA.dump(Polling.query.filter_by(id=1).first()))


@api.route('/getPollHistory/<host_id>', methods=['GET'])
def get_poll_history(host_id):
    '''Get poll history for a single host'''
    return json.dumps(POLL_HISTORY_SCHEMA.dump(PollHistory.query.filter_by(host_id=host_id)))


@api.route('/getAlertsEnabled', methods=['GET'])
def get_alerts_enabled():
    '''Get whether alerts are enabled or not'''
    status = USER_SCHEMA.dump(Users.query.first())['alerts_enabled']
    return json.dumps({'alerts_enabled': status})


@api.route('/getSmtpConfigured', methods=['GET'])
def get_smtp_configured():
    '''Get whether SMTP configured or not'''
    if SMTP_SCHEMA.dump(SmtpServer.query.first()):
        return json.dumps({'smtp_configured': True})
    
    return json.dumps({'smtp_configured': False})


@api.route('/getWebThemes', methods=['GET'])
def get_web_themes():
    '''Get all web themese'''

    return json.dumps(WEB_THEMES_SCHEMA.dump(WebThemes.query.all()))


@api.route('/getActiveTheme', methods=['GET'])
def get_active_theme():
    '''Get active theme'''
    return json.dumps(WEB_THEME_SCHEMA.dump(WebThemes.query.filter_by(active=True).first()))


@api.route('/getHostCounts', methods=['GET'])
def get_host_counts():
    '''Get host total, available, unavailable host counts'''
    total = Hosts.query.count()
    num_up = Hosts.query.filter(Hosts.status == 'Up').count()
    num_down = Hosts.query.filter(Hosts.status == 'Down').count()

    return json.dumps({'total_hosts': total, 'available_hosts': num_up, 'unavailable_hosts': num_down})
