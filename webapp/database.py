'''Database File'''
import os
import sys

from datetime import datetime
from marshmallow import Schema

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
from webapp import db

##########################
# Models ################
##########################
class Users(db.Model):
    '''Users table'''
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(length=20), nullable=False, unique=True)
    email = db.Column(db.String(length=50), nullable=False, unique=True)
    password = db.Column(db.String(length=200), nullable=False)
    date_created = db.Column(db.Date, default=datetime.now())
    alerts_enabled = db.Column(db.Boolean, default=True)

class UserSchema(Schema):
    '''Users schema'''
    class Meta:
        '''Metadata'''
        fields = ('id', 'username', 'password', 'email', 'date_created', 'alerts_enabled')


class Hosts(db.Model):
    '''Hosts'''
    __tablename__ = 'hosts'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(length=15), nullable=False, unique=True)
    hostname = db.Column(db.String(length=100))
    status = db.Column(db.String(length=10))
    last_poll = db.Column(db.String(length=20))
    previous_status = db.Column(db.String(length=10))
    status_change_alert = db.Column(db.Boolean, default=False)
    poll_history = db.relationship("PollHistory")


class HostsSchema(Schema):
    '''Hosts Schema'''
    class Meta:
        '''Meta'''
        fields = ('id', 'ip_address', 'hostname', 'status', 'last_poll', 'status_change_alert')


class PollHistory(db.Model):
    '''Poll history for hosts'''
    __tablename__ = 'pollHistory'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    host_id = db.Column(db.Integer, db.ForeignKey('hosts.id'))
    poll_time = db.Column(db.String(length=20))
    poll_status = db.Column(db.String(length=20))
    date_created = db.Column(db.Date, default=datetime.now())


class PollHistorySchema(Schema):
    '''Poll History Schema'''
    class Meta:
        '''Meta'''
        fields = ('id', 'host_id', 'poll_time', 'poll_status', 'date_created')


class Polling(db.Model):
    '''Polling Config'''
    __tablename__ = 'polling'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    poll_interval = db.Column(db.Integer, default=60, nullable=False)
    history_truncate_days = db.Column(db.Integer, default=10, nullable=False)


class PollingSchema(Schema):
    '''Polling Schema'''
    class Meta:
        '''Meta'''
        fields = ('id', 'poll_interval', 'history_truncate_days')


class SmtpServer(db.Model):
    '''SMTP Server'''
    __tablename__ = 'smtp'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    smtp_server = db.Column(db.String(length=100), nullable=False)
    smtp_port = db.Column(db.Integer, nullable=False)
    smtp_sender = db.Column(db.String(length=100), nullable=False)


class SmtpSchema(Schema):
    '''SMTP Schema'''
    class Meta:
        '''Meta'''
        fields = ('id', 'smtp_server', 'smtp_port', 'smtp_sender')


class WebThemes(db.Model):
    '''Web CSS Themese'''
    __tablename = 'webThemes'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    theme_name = db.Column(db.String(length=100), nullable=False)
    theme_path = db.Column(db.String(length=100), nullable=False)
    active = db.Column(db.Boolean, default=False)


class WebThemesSchema(Schema):
    '''Web Theme Schema'''
    class Meta:
        '''Meta'''
        fields = ('id', 'theme_name', 'theme_path', 'active')


##########################
# Schemas ################
##########################
USER_SCHEMA = UserSchema()
HOST_SCHEMA = HostsSchema()
HOSTS_SCHEMA = HostsSchema(many=True)
POLL_HISTORY_SCHEMA = PollHistorySchema(many=True)
POLLING_SCHEMA = PollingSchema()
SMTP_SCHEMA = SmtpSchema()
WEB_THEME_SCHEMA = WebThemesSchema()
WEB_THEMES_SCHEMA = WebThemesSchema(many=True)
