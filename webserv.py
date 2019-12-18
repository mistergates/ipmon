'''Runs the web server on localhost, port 80'''
import os
import sys
import json
import atexit
import argparse
import logging

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from webapp import app, config, log
from webapp.main import get_polling_config
from webapp.main import main as main_blueprint
from webapp.auth import auth as auth_blueprint
from webapp.smtp import smtp as smtp_blueprint
from webapp.api import api as api_blueprint
from webapp.hosts import hosts as hosts_blueprint
from webapp.setup import bp as setup_blueprint

parser = argparse.ArgumentParser(description='Web Server Arguments')
parser.add_argument('--host', type=str, default='0.0.0.0', help="Binds the server to this hostname/IP address")
parser.add_argument('--port', type=int, default=80, help="Binds the server to this port")
parser.add_argument('--debug', action="store_true", default=False, help="Runs the server in debug mode")
args = parser.parse_args()

if __name__ == '__main__':
    # if not os.path.exists(config['Database_Path']):
    #     raise Exception(
    #         'Database does not exist. Run "python {}"'.format(
    #             os.path.join(
    #                 os.path.dirname(os.path.realpath(__file__)),
    #                 'setup.py'
    #             )
    #         )
    #     )

    # Register blueprints
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(smtp_blueprint)
    app.register_blueprint(api_blueprint)
    app.register_blueprint(hosts_blueprint)
    app.register_blueprint(setup_blueprint)


    # Enable debug logging if debug arg provided
    log.setLevel(logging.DEBUG if args.debug else logging.INFO)

    # Run Server
    app.run(host=args.host, port=args.port, debug=args.debug)
