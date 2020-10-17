'''Web Forms'''
import os
import sys

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, NumberRange

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
from ipmon import config


class FirstTimeSetupForm(FlaskForm):
    password_policy = 'Password Policy: Minimum Length ({}), Minimum Uppercase ({}), Minimum Non-Letters ({}).'.format(
        config['Password_Policy']['Length'],
        config['Password_Policy']['Uppercase'],
        config['Password_Policy']['Nonletters']
    )
    username = StringField('Username', validators=[DataRequired(message="Username required")])
    email = StringField('Email Address', validators=[DataRequired(message="Email address required"), Email(message="Invalid email address")])
    password = PasswordField('Password', description=password_policy, validators=[DataRequired(message="New password required")])
    verify_password = PasswordField('Verify Password', validators=[DataRequired(message="Password verification required")])
    poll_interval = IntegerField('Polling Interval (Seconds)', validators=[DataRequired(message="Polling interval required")])
    retention_days = IntegerField('Poll History Retention (Days)', validators=[DataRequired(message="Poll history retention required")])
    enable_smtp = BooleanField('Enable SMTP Alerts')
    smtp_server = StringField('Server')
    smtp_port = StringField('Port')
    smtp_sender = StringField('Sender Address')
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(message="Username required")])
    password = PasswordField('Password', validators=[DataRequired(message="Password required")])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdatePasswordForm(FlaskForm):
    desc = 'Password Policy: Minimum Length ({}), Minimum Uppercase ({}), Minimum Non-Letters ({}).'.format(
        config['Password_Policy']['Length'],
        config['Password_Policy']['Uppercase'],
        config['Password_Policy']['Nonletters']
    )
    current_password = PasswordField('Current Password', validators=[DataRequired(message="Current password required")])
    new_password = PasswordField('New Password', description=desc, validators=[DataRequired(message="New password required")])
    verify_password = PasswordField('Verify Password', validators=[DataRequired(message="Password verification required")])
    submit = SubmitField('Update')


class UpdateEmailForm(FlaskForm):
    email = StringField('New Email Address', validators=[DataRequired(message="Email address required"), Email(message="Invalid email address")])
    email_verify = StringField('Verify Email Address', validators=[DataRequired(message="Verify Email address required"), Email(message="Invalid email address")])
    password = PasswordField('Password', validators=[DataRequired(message="Password required")])
    submit = SubmitField('Update')


class SmtpConfigForm(FlaskForm):
    server = StringField('Server', validators=[DataRequired(message="Server required")])
    port = IntegerField('Port', validators=[DataRequired(message="Port required"), NumberRange(min=0, message="Invalid port number")])
    sender = StringField('Sender Address', validators=[DataRequired(message="Sender address required"), Email(message="Invalid email address")])
    submit = SubmitField('Update')


class AddHostsForm(FlaskForm):
    ip_address = TextAreaField('IP Addresses', validators=[DataRequired(message="IP Address required")])
    submit = SubmitField('Add')


class SelectThemeForm(FlaskForm):
    theme = SelectField('Theme', config['Web_Themes'].items())
    submit = SubmitField('Update')


class PollingConfigForm(FlaskForm):
    interval = StringField('Polling Interval')
    retention_days = StringField('Poll History Retention Days')
    submit = SubmitField('Update')
