'''Package init file'''
import os
import flask_login

from flask_apscheduler import APScheduler
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

config = {
    'Database_Name': 'sqlite.db'
}

config['Database_Path'] =  os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'db',
    config['Database_Name']
)

app = Flask(__name__)
app.secret_key = os.urandom(12)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(config['Database_Path'])

db = SQLAlchemy()
db.init_app(app)

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

login_manager = flask_login.LoginManager()
login_manager.init_app(app)
