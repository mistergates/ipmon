'''SMTP Library'''
import os
import sys
import flask_login
import smtplib

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
from webapp import db
from webapp.database import SmtpServer, SMTP_SCHEMA

from passlib.hash import sha256_crypt
from email.mime.text import MIMEText
from flask import Blueprint, render_template, redirect, url_for, request, flash

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
            smtp_conf.smtp_server = results['smtp_server']
            smtp_conf.smtp_port = results['smtp_port']
            smtp_conf.smtp_sender = results['smtp_sender']
            # if results['smtp_password']:
            #     smtp_conf.smtp_password = sha256_crypt.hash(results['smtp_password'])
            db.session.commit()
            flash('Successfully updated SMTP configuration', 'success')
        except Exception:
            flash('Failed to update SMTP configuration', 'danger')

        return redirect(url_for('smtp.smtp_config'))


@smtp.route("/smtpTest", methods=['POST'])
@flask_login.login_required
def smtp_test():
    '''Send SMTP test email'''
    if request.method == 'POST':
        results = request.form.to_dict()
        subject = 'IP Monitoring SMTP Test'
        message = 'IP Monitoring SMTP Test'
        # message = 'IP Monitoring SMTP Test'

        try:
            _send_smtp_message(results['recipient'], subject, message)
            flash('Successfully sent SMTP test', 'success')
        except Exception as exc:
            flash('Failed to send SMTP test: {}'.format(exc), 'danger')

    return redirect(url_for('smtp.smtp_config'))


##########################
# Private Functions ######
##########################
def _send_smtp_message(recipient, subject, message):
    current_smtp = SMTP_SCHEMA.dump(SmtpServer.query.first())

    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = current_smtp['smtp_sender']

    server = smtplib.SMTP(current_smtp['smtp_server'], current_smtp['smtp_port'])

    # Secure the connection
    server.starttls()

    # Send ehlo
    server.ehlo()
    # server.set_debuglevel(False)

    # Login if password was provided
    if current_smtp['smtp_password']:
        server.login(current_smtp['smtp_sender'], current_smtp['smtp_password'])

    # Send message
    server.sendmail(current_smtp['smtp_sender'], recipient, msg.as_string())
    server.quit()
