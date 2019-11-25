'''Web Forms'''
import os
import sys

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, TextAreaField, SelectField
from wtforms.validators import DataRequired, IPAddress, Email

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
from webapp import config


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(message="Username required")])
    password = PasswordField('Password', validators=[DataRequired(message="Password required")])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')


class SmtpConfigForm(FlaskForm):
    server = StringField('Username', validators=[DataRequired(message="Server required")])
    port = IntegerField('Password', validators=[DataRequired(message="Port required")])
    sender_address = StringField('Password', validators=[DataRequired(message="Sender address required"), Email(message="Invalid email address")])
    submit = SubmitField('Update')


class AddHostsForm(FlaskForm):
    ip_address = TextAreaField('IP Addresses', validators=[DataRequired(message="IP Address required")])
    submit = SubmitField('Add')


class UpdateHostForm(FlaskForm):
    hostname = StringField('Username')
    ip_address = TextAreaField('IP Addresses', validators=[IPAddress(ipv6=True, message="Invalid IP address")])
    submit = SubmitField('Update')


class SelectThemeForm(FlaskForm):
    theme = SelectField('Theme', config['Web_Themes'].items())
    submit = SubmitField('Update')

