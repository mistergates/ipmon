'''Database File'''
import os
import sys

from datetime import datetime

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
from ipmon import db

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
    alerts_enabled = db.Column(db.Boolean, default=True)
    poll_history = db.relationship("PollHistory")
    alerts = db.relationship("HostAlerts")


class PollHistory(db.Model):
    '''Poll history for hosts'''
    __tablename__ = 'pollHistory'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    poll_time = db.Column(db.String(length=20))
    poll_status = db.Column(db.String(length=20))
    date_created = db.Column(db.Date, default=datetime.now())
    host_id = db.Column(db.Integer, db.ForeignKey('hosts.id'))


class HostAlerts(db.Model):
    '''Alerts For Host Status Change'''
    __tablename__ = 'hostAlerts'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(length=100))
    ip_address = db.Column(db.String(length=15))
    host_status = db.Column(db.String(length=20))
    poll_time = db.Column(db.String(length=20))
    alert_cleared = db.Column(db.Boolean, default=False)
    date_created = db.Column(db.Date, default=datetime.now())
    host_id = db.Column(db.Integer, db.ForeignKey('hosts.id'))


class Polling(db.Model):
    '''Polling Config'''
    __tablename__ = 'polling'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    poll_interval = db.Column(db.Integer, default=60, nullable=False)
    history_truncate_days = db.Column(db.Integer, default=10, nullable=False)


class SmtpServer(db.Model):
    '''SMTP Server'''
    __tablename__ = 'smtp'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    smtp_server = db.Column(db.String(length=100), nullable=False)
    smtp_port = db.Column(db.Integer, nullable=False)
    smtp_sender = db.Column(db.String(length=100), nullable=False)


class WebThemes(db.Model):
    '''Web CSS Themese'''
    __tablename = 'webThemes'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    theme_name = db.Column(db.String(length=100), nullable=False)
    theme_path = db.Column(db.String(length=100), nullable=False)
    active = db.Column(db.Boolean, default=False)
