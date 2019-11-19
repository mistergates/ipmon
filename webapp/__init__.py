'''Package init file'''
import os
import flask_login

from flask_sqlalchemy import SQLAlchemy
from flask import Flask

config = {
    'Database_Name': 'sqlite.db'
}

app = Flask(__name__)
app.secret_key = os.urandom(12)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        config['Database_Name']
    )
)

db = SQLAlchemy()
db.init_app(app)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)
