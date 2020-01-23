'''Package init file'''
import os
import logging
import flask_login
import tempfile
import time
import uuid

from password_strength import PasswordPolicy
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template
from flask_migrate import Migrate
from apscheduler.schedulers.background import BackgroundScheduler


config = {
    'Database_Path': os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'database',
        'ipmon.db'
    ),
    'Web_Themes': {
        'Darkly (Dark/Dark Blue)': '/static/css/darkly.min.css',
        'Cyborg (Dark/Light Blue)': '/static/css/cyborg.min.css',
        'Slate (Dark/Grey)': '/static/css/slate.min.css',
        'Simplix (Light/Red)': '/static/css/simplix.min.css',
        'Flatly (Light/Dark Blue)': '/static/css/flatly.min.css'
    },
    'Password_Policy': {
        'Length': 8,
        'Uppercase': 1,
        'Nonletters': 2
    },
    'Max_Threads': 100
}

# Web App
app = Flask(__name__)
app.secret_key = str(uuid.UUID(int=uuid.getnode()))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(config['Database_Path'])

# Database
db = SQLAlchemy()
db.init_app(app)

# Database Migration
migrate = Migrate(app, db)

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


# Register Blueprints
from ipmon.main import main as main_blueprint
from ipmon.auth import auth as auth_blueprint
from ipmon.smtp import smtp as smtp_blueprint
from ipmon.api import api as api_blueprint
from ipmon.hosts import hosts as hosts_blueprint
from ipmon.setup import bp as setup_blueprint

app.register_blueprint(main_blueprint)
app.register_blueprint(auth_blueprint)
app.register_blueprint(smtp_blueprint)
app.register_blueprint(api_blueprint)
app.register_blueprint(hosts_blueprint)
app.register_blueprint(setup_blueprint)
