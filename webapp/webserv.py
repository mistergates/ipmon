'''Runs the web server on localhost, port 80'''
import os
import sys

from flask import render_template
from werkzeug.exceptions import HTTPException, default_exceptions
from flask_apscheduler import APScheduler

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
from webapp import app
from webapp.main import main as main_blueprint
from webapp.auth import auth as auth_blueprint
from webapp.smtp import smtp as smtp_blueprint
from webapp.main import poll_hosts


class Config(object):
    JOBS = [
        {
            'id': 'hostPolling',
            'func': 'jobs:poll_hosts',
            'trigger': 'interval',
            'seconds': 10
        }
    ]
    SCHEDULER_API_ENABLED = True


def handle_error(error):
    '''Global Error Handler'''
    print('ERROR: {}'.format(error))
    code = 500
    desc = 'Internal Server Error'
    if isinstance(error, HTTPException):
        code = error.code
        desc = error.description
    return render_template('error.html', code=code, desc=desc)


if __name__ == '__main__':
    # Register blueprints
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(smtp_blueprint)

    # Register error handling
    for cls in HTTPException.__subclasses__():
        app.register_error_handler(cls, handle_error)

    # Start server polling threaded
    scheduler = APScheduler()
    # it is also possible to enable the API directly
    # scheduler.api_enabled = True
    scheduler.init_app(app)
    scheduler.start()

    # Run Server
    app.run(port=80, debug=True)
