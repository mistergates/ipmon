'''Runs the web server on localhost, port 80'''
import os
import sys
import json

from flask import render_template
from werkzeug.exceptions import HTTPException

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
from webapp import app
from webapp.host_polling import poll_hosts
from webapp.main import get_polling_interval
from webapp.main import main as main_blueprint
from webapp.auth import auth as auth_blueprint
from webapp.smtp import smtp as smtp_blueprint


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

    # Get polling time
    with app.app_context():
        poll_interval = int(json.loads(get_polling_interval())['poll_interval'])

    # Start server polling via APScheduler
    app.apscheduler.add_job(id='Poll Hosts', func=poll_hosts, trigger='interval', seconds=poll_interval)

    # Run Server
    app.run(port=80, debug=True)
