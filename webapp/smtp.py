'''SMTP Library'''
import os
import sys
import flask_login
import smtplib

from email.mime.text import MIMEText
from flask import Blueprint, render_template, redirect, url_for, request, flash

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
from webapp import db, scheduler, app
from webapp.database import SmtpServer, SMTP_SCHEMA, Users, USER_SCHEMA, Hosts
from webapp.main import get_alerts_enabled

smtp = Blueprint('smtp', __name__)


##########################
# Routes #################
##########################
@smtp.route("/smtpConfig", methods=['GET', 'POST'])
@flask_login.login_required
def smtp_config():
    '''SMTP Config'''
    if request.method == 'GET':
        current_smtp = SMTP_SCHEMA.dump(SmtpServer.query.first())
        return render_template('smtpConfig.html', smtp=current_smtp)
    elif request.method == 'POST':
        results = request.form.to_dict()
        try:
            smtp_conf = SmtpServer.query.filter_by(id='1').first()
            if not smtp_conf:
                smtp_conf = SmtpServer(
                    smtp_server=results['smtp_server'],
                    smtp_port=results['smtp_port'],
                    smtp_sender=results['smtp_sender']
                )
                db.session.add(smtp_conf)
            else:
                smtp_conf.smtp_server = results['smtp_server']
                smtp_conf.smtp_port = results['smtp_port']
                smtp_conf.smtp_sender = results['smtp_sender']
            db.session.commit()
            flash('Successfully updated SMTP configuration', 'success')
        except Exception as exc:
            flash('Failed to update SMTP configuration: {}'.format(exc), 'danger')

        return redirect(url_for('smtp.smtp_config'))


@smtp.route("/smtpTest", methods=['POST'])
@flask_login.login_required
def smtp_test():
    '''Send SMTP test email'''
    if request.method == 'POST':
        results = request.form.to_dict()
        subject = 'IPMON SMTP Test Message'
        message = 'IPMON SMTP Test Message'

        try:
            _send_smtp_message(results['recipient'], subject, message)
            flash('Successfully sent SMTP test message', 'success')
        except Exception as exc:
            flash('Failed to send SMTP test message: {}'.format(exc), 'danger')

    return redirect(url_for('smtp.smtp_config'))


def host_status_change_alerts():
    '''Send SMTP alert if host statuses have changed'''
    with app.app_context():
        if get_alerts_enabled() and _smtp_enabled():
            message = ''
            for host in Hosts.query.filter_by(status_change_alert=True):
                message += '{} [{}] Status changed from {} to {} at {}\n\n'.format(
                    host.hostname,
                    host.ip_address,
                    host.previous_status,
                    host.status,
                    host.last_poll
                )
                # Set status_change_alert to False so we don't send duplicated alerts
                host.status_change_alert = False

            db.session.commit()

            if message:
                print('Sending SMTP Alert')
                _send_smtp_message(
                    recipient=USER_SCHEMA.dump(Users.query.filter_by(id='1').first())['email'],
                    subject='IPMON - Host Status Change Alert',
                    message='{} [{}] Status changed from {} to {} at {}.'.format(
                        host.hostname,
                        host.ip_address,
                        host.previous_status,
                        host.status,
                        host.last_poll
                    )
                )


def update_status_change_alert_schedule(alert_interval):
    '''Updates the PHost Status Change Alert schedula via APScheduler'''
    # Attempt to remove the current scheduler
    try:
        scheduler.scheduler.remove_job('Host Status Change Alert')
    except Exception:
        pass

    scheduler.scheduler.add_job(id='Host Status Change Alert', func=host_status_change_alerts, trigger='interval', seconds=int(alert_interval), max_instances=1)


##########################
# Private Functions ######
##########################
def _send_smtp_message(recipient, subject, message):
    current_smtp = SMTP_SCHEMA.dump(SmtpServer.query.first())

    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = current_smtp['smtp_sender']

    server = smtplib.SMTP(current_smtp['smtp_server'], current_smtp['smtp_port'], timeout=10)

    # Secure the connection
    server.starttls()

    # Send ehlo
    server.ehlo()
    server.set_debuglevel(False)

    # Send message
    server.sendmail(current_smtp['smtp_sender'], recipient, msg.as_string())
    server.quit()

def _smtp_enabled():
    smtp_conf = SmtpServer.query.filter_by(id='1').first()
    if not smtp_conf:
        return False
    else:
        return True
