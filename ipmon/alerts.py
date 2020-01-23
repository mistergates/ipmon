'''Alerts Module'''
import os
import sys
import json

from multiprocessing.pool import ThreadPool

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
from ipmon import db, scheduler, app, config, log
from ipmon.database import Users, Hosts, HostAlerts
from ipmon.schemas import Schemas
from ipmon.api import get_alerts_enabled, get_smtp_configured
from ipmon.smtp import send_smtp_message


def update_host_status_alert_schedule(alert_interval):
    '''Updates the PHost Status Change Alert schedula via APScheduler'''
    # Attempt to remove the current scheduler
    try:
        scheduler.remove_job('Host Status Change Alert')
    except Exception:
        pass

    scheduler.add_job(id='Host Status Change Alert', func=_host_status_alerts_threaded, trigger='interval', seconds=int(alert_interval), max_instances=1)


def _host_status_alerts_threaded():
    with app.app_context():
        alerts_enabled = json.loads(get_alerts_enabled())['alerts_enabled']
        smtp_configured = json.loads(get_smtp_configured())['smtp_configured']
        alerts = HostAlerts.query.filter_by(alert_cleared=False).all()

        for alert in alerts:
            alert.alert_cleared = True

        if smtp_configured and alerts_enabled:
            pool = ThreadPool(config['Max_Threads'])
            threads = []

            message = ''
            for alert in alerts:
                threads.append(
                    pool.apply_async(_get_alert_status_message, (alert,))
                )

            pool.close()
            pool.join()

            for thread in threads:
                message += thread.get()

            if message:
                recipients = ';'.join(x['email'] for x in Schemas.users(many=True).dump(Users.query.filter_by(alerts_enabled=True)))
                try:
                    send_smtp_message(
                        recipient=recipients,
                        subject='IPMON - Host Status Change Alert',
                        message=message
                    )
                except Exception as exc:
                    log.error('Failed to send host status change alert email: {}'.format(exc))

        db.session.commit()


def _get_alert_status_message(alert):
    with app.app_context():
        host = Hosts.query.filter_by(id=alert.host_id).first()
        message = '<b>{} [{}]</b>: Status changed from <b>"{}"</b> to <b>"{}"</b> at {}<br><br>'.format(
            host.hostname,
            host.ip_address,
            host.previous_status,
            host.status,
            host.last_poll
        )

        return message
