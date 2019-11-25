'''Runs the web server on localhost, port 80'''
import os
import sys
import json
import atexit
import argparse

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from webapp import app, scheduler, config
from webapp.polling import update_poll_scheduler
from webapp.smtp import update_status_change_alert_schedule
from webapp.main import get_polling_config
from webapp.main import main as main_blueprint
from webapp.auth import auth as auth_blueprint
from webapp.smtp import smtp as smtp_blueprint
from webapp.api import api as api_blueprint
from webapp.hosts import hosts as hosts_blueprint

parser = argparse.ArgumentParser(description='Web Server Arguments')
parser.add_argument('--host', type=str, default='127.0.0.1', help="Binds the server to this hostname/IP address")
parser.add_argument('--port', type=int, default=80, help="Binds the server to this port")
parser.add_argument('--debug', action="store_true", default=False, help="Runs the server in debug mode")
args = parser.parse_args()

if __name__ == '__main__':
    if not os.path.exists(config['Database_Path']):
        raise Exception(
            'Database does not exist. Run "python {}"'.format(
                os.path.join(
                    os.path.dirname(os.path.realpath(__file__)),
                    'setup.py'
                )
            )
        )

    # Register blueprints
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(smtp_blueprint)
    app.register_blueprint(api_blueprint)
    app.register_blueprint(hosts_blueprint)

    # Get polling interval
    with app.app_context():
        poll_interval = int(json.loads(get_polling_config())['poll_interval'])

    # Add scheduled jobs
    update_poll_scheduler(poll_interval)
    update_status_change_alert_schedule(poll_interval / 2)

    # Shut down the scheduler when exiting the app
    atexit.register(scheduler.shutdown)

    # Run Server
    app.run(host=args.host, port=args.port, debug=args.debug)
