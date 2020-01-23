'''SMTP Library'''
import os
import sys
import smtplib
import json

import flask_login
from email.mime.text import MIMEText
from flask import Blueprint, render_template, redirect, url_for, request, flash

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
from ipmon import db, log
from ipmon.database import SmtpServer
from ipmon.api import get_smtp_configured, get_smtp_config
from ipmon.forms import SmtpConfigForm

smtp = Blueprint('smtp', __name__)


##########################
# Routes #################
##########################
@smtp.route("/configureSMTP", methods=['GET', 'POST', 'DELETE'])
@flask_login.login_required
def configure_smtp():
    '''SMTP Config'''
    form = SmtpConfigForm()
    if request.method == 'GET':
        return render_template('smtpConfig.html', smtp=json.loads(get_smtp_config()), form=form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            try:
                smtp_conf = SmtpServer.query.first()
                smtp_conf.smtp_server = form.server.data
                smtp_conf.smtp_port = form.port.data
                smtp_conf.smtp_sender = form.sender.data
                db.session.commit()
                flash('Successfully updated SMTP configuration', 'success')
            except Exception as exc:
                flash('Failed to update SMTP configuration: {}'.format(exc), 'danger')
        else:
            for dummy, errors in form.errors.items():
                for error in errors:
                    flash(error, 'danger')
    elif request.method == 'DELETE':
        try:
            smtp_conf = SmtpServer.query.first()
            smtp_conf.smtp_server = ''
            smtp_conf.smtp_port = ''
            smtp_conf.smtp_sender = ''
            db.session.commit()
            flash('Successfully removed SMTP configuration', 'success')
        except Exception:
            flash('Failed to remove SMTP configuration', 'danger')

    return redirect(url_for('smtp.configure_smtp'))


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

    return redirect(url_for('smtp.configure_smtp'))


##########################
# Functions ##############
##########################
def send_smtp_message(recipient, subject, message):
    '''Send SMTP message'''
    current_smtp = json.loads(get_smtp_config())

    if not json.loads(get_smtp_configured())['smtp_configured']:
        log.error('Attempting to send SMTP message but SMTP not configured.')
        return

    msg = MIMEText(message, 'html')
    msg['Subject'] = subject
    msg['From'] = current_smtp['smtp_sender']

    try:
        server = smtplib.SMTP(current_smtp['smtp_server'], current_smtp['smtp_port'], timeout=10)
    except Exception as exc:
        log.error('Failed to start SMTP server: {}'.format(exc))
        raise exc

    # Secure the connection
    server.starttls()

    # Send ehlo
    server.ehlo()
    server.set_debuglevel(False)

    # Send message
    server.sendmail(current_smtp['smtp_sender'], recipient, msg.as_string())
    server.quit()
