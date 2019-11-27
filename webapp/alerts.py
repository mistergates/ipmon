'''Alerts Module'''
import os
import sys
import json

from multiprocessing.pool import ThreadPool

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
from webapp import db, scheduler, app, config
from webapp.database import Users, Hosts, HostAlerts, Schemas
from webapp.api import get_alerts_enabled, get_smtp_configured
from webapp.smtp import send_smtp_message


def update_host_status_alert_schedule(alert_interval):
    '''Updates the PHost Status Change Alert schedula via APScheduler'''
    # Attempt to remove the current scheduler
    try:
        scheduler.remove_job('Host Status Change Alert')
    except Exception:
        pass

    scheduler.add_job(id='Host Status Change Alert', func=_host_status_alerts_threaded, trigger='interval', seconds=int(alert_interval), max_instances=1)


def _host_status_alerts_threaded():
    pool = ThreadPool(config['Max_Threads'])
    threads = []

    with app.app_context():
        alerts_enabled = json.loads(get_alerts_enabled())['alerts_enabled']
        smtp_configured = json.loads(get_smtp_configured())['smtp_configured']
        alerts = HostAlerts.query.filter_by(alert_cleared=False).all()

        for alert in alerts:
            alert.alert_cleared = True

        if smtp_configured and alerts_enabled:
            message = ''
            for alert in alerts:
                threads.append(
                    pool.apply_async(_get_alert_status_message, (alert,))
                )

            for thread in threads:
                message += thread.get()

            if message:
                send_smtp_message(
                    recipient=Schemas.USER_SCHEMA.dump(Users.query.filter_by(id='1').first())['email'],
                    subject='IPMON - Host Status Change Alert',
                    message=message
                )

        db.session.commit()


def _get_alert_status_message(alert):
    with app.app_context():
        host = Hosts.query.filter_by(id=alert.host_id).first()
        message = '{} [{}] Status changed from {} to {} at {}\n\n'.format(
            host.hostname,
            host.ip_address,
            host.previous_status,
            host.status,
            host.last_poll
        )

        return message
