'''SMTP Library'''
import os
import sys
import flask_login
import smtplib

from email.mime.text import MIMEText
from flask import Blueprint, render_template, redirect, url_for, request, flash

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
from webapp import db
from webapp.database import SmtpServer, Schemas
from webapp.api import get_alerts_enabled, get_smtp_configured

smtp = Blueprint('smtp', __name__)


##########################
# Routes #################
##########################
@smtp.route("/smtpConfig", methods=['GET', 'POST'])
@flask_login.login_required
def smtp_config():
    '''SMTP Config'''
    if request.method == 'GET':
        current_smtp = Schemas.SMTP_SCHEMA.dump(SmtpServer.query.first())
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
            send_smtp_message(results['recipient'], subject, message)
            flash('Successfully sent SMTP test message', 'success')
        except Exception as exc:
            flash('Failed to send SMTP test message: {}'.format(exc), 'danger')

    return redirect(url_for('smtp.smtp_config'))


##########################
# Functions ##############
##########################
def send_smtp_message(recipient, subject, message):
    '''Send SMTP message'''
    current_smtp = Schemas.SMTP_SCHEMA.dump(SmtpServer.query.first())

    if not current_smtp:
        log.error('Attempting to send SMTP message but SMTP not configured.')
        return

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
