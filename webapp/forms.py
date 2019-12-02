'''Web Forms'''
import os
import sys

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, NumberRange

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
from webapp import config


class FirstTimeSetupForm(FlaskForm):
    password_policy = 'Password Policy: Minimum Length ({}), Minimum Uppercase ({}), Minimum Non-Letters ({}).'.format(
        config['Password_Policy']['Length'],
        config['Password_Policy']['Uppercase'],
        config['Password_Policy']['Nonletters']
    )
    username = StringField('Username', validators=[DataRequired(message="Username required")])
    email = StringField('Email Address', validators=[DataRequired(message="Sender address required"), Email(message="Invalid email address")])
    password = PasswordField('Password', description=password_policy, validators=[DataRequired(message="New password required")])
    verify_password = PasswordField('Verify Password', validators=[DataRequired(message="Password verification required")])
    interval = StringField('Polling Interval')
    retention_days = StringField('Poll History Retention Days')
    enable_smtp = BooleanField('Enable SMTP Alerts')
    smtp_server = StringField('Server', validators=[DataRequired(message="Server required")])
    smtp_port = IntegerField('Port', validators=[DataRequired(message="Port required"), NumberRange(min=0, message="Invalid port number")])
    smtp_sender = StringField('Sender Address', validators=[DataRequired(message="Sender address required"), Email(message="Invalid email address")])
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
