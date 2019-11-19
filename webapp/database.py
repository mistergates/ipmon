'''Database File'''
import os
import sys

from datetime import datetime
from marshmallow import Schema

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
from webapp import db


class Users(db.Model):
    '''Users table'''
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(length=20), nullable=False, unique=True)
    email = db.Column(db.String(length=50), nullable=False, unique=True)
    password = db.Column(db.String(length=100), nullable=False)
    date_created = db.Column(db.Date, default=datetime.now())


class Hosts(db.Model):
    '''Hosts'''
    __tablename__ = 'hosts'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(length=15), nullable=False, unique=True)
    hostname = db.Column(db.String(length=100))
    status = db.Column(db.String(length=10))
    last_poll = db.Column(db.String(length=20))


##########################
# Schemas ################
##########################
class UserSchema(Schema):
    '''Users schema'''
    class Meta:
        '''Metadata'''
        fields = ('id', 'username', 'password', 'email', 'date_created')


class HostsSchema(Schema):
    '''Hosts Schema'''
    class Meta:
        '''Meta'''
        fields = ('id', 'ip_address', 'hostname', 'status', 'last_poll')


USER_SCHEMA = UserSchema()
HOST_SCHEMA = HostsSchema()
HOSTS_SCHEMA = HostsSchema(many=True)
