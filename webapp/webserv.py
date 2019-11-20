'''Runs the web server on localhost, port 80'''
import os
import sys
import json
import atexit

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
from webapp import app, scheduler
from webapp.host_polling import update_poll_scheduler
from webapp.main import get_polling_interval
from webapp.main import main as main_blueprint
from webapp.auth import auth as auth_blueprint
from webapp.smtp import smtp as smtp_blueprint


if __name__ == '__main__':
    # Register blueprints
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(smtp_blueprint)

    # Get polling interval
    with app.app_context():
        poll_interval = int(json.loads(get_polling_interval())['poll_interval'])

    # Start server polling via APScheduler
    update_poll_scheduler(poll_interval)

    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())

    # Run Server
    app.run(port=80, debug=True)
