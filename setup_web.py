'''Setup File Script

This stands up a quick Flask Webapp to configure our main app
'''
import os
import sys
import uuid
import webbrowser
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

# try:
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt
from sqlalchemy import create_engine

from webapp import config
from webapp.forms import FirstTimeSetupForm
# except ImportError:
    # print('\nFailed to load required modules. Try running "pip install -r {}" from command line.\n'.format(
    #     os.path.join(
    #         os.path.dirname(os.path.realpath(__file__)),
    #         'requirements.txt'
    #         )
    # ))
    # sys.exit(1)


app = Flask(__name__)
app.secret_key = str(uuid.UUID(int=uuid.getnode()))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(config['Database_Path'])
db = SQLAlchemy()
db.init_app(app)


@app.route('/')
def home():
    return redirect(url_for('setup'))


@app.route('/setup')
def setup():
    form = FirstTimeSetupForm()
    html = """
<html>
<head>
    <title>IPMON Setup</title>
</head>
<body>
    <form method="POST" action="/setup" novalidate>
        <h1>Admin User Setup</h1>
        {0}<br>{1}
""".format(
    form.username.label(),
    form.username()
)
    return html


if __name__ == '__main__':
    webbrowser.open('http://127.0.0.1:8080/setup')
    app.run(host='127.0.0.1', port=8080, debug=False)
