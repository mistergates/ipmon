'''Package init file'''
import os
import logging
import flask_login
import tempfile
import time

from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template
from apscheduler.schedulers.background import BackgroundScheduler


config = {
    'Database_Path': os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'database',
        'sqlite.db'
    ),
    'Web_Themes': {
        'Dark': '/static/css/slate.min.css',
        'Light': '/static/css/simplix.min.css',
        'Classic': '/static/css/flastly.min.css'
    },
    'Max_Threads': 100,
    'Alerts_Poll': 10
}

# Web App
app = Flask(__name__)
app.secret_key = os.urandom(12)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(config['Database_Path'])

# Database
db = SQLAlchemy()
db.init_app(app)

# Scheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Authentication Manager
login_manager = flask_login.LoginManager()
login_manager.init_app(app)


# Create logger
log = logging.getLogger('IPMON')
console = logging.StreamHandler()
console_format = '%(asctime)s [%(levelname)s] - %(message)s'
console.setFormatter(logging.Formatter(console_format, '%Y-%m-%d %H:%M:%S'))
log.addHandler(console)
logfile = os.path.join(
    tempfile.gettempdir(),
    'IPMON_{}.log'.format(time.strftime("%Y%m%d-%H%M%S"))
)
file_handler = logging.FileHandler(logfile)
logfile_format = '%(asctime)s [%(levelname)s] <%(filename)s:%(lineno)s> - %(message)s'
file_handler.setFormatter(logging.Formatter(logfile_format, '%Y-%m-%d %H:%M:%S'))
log.addHandler(file_handler)
