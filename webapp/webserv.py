'''Runs the web server on localhost, port 80'''
import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
from webapp import app
from webapp.main import main as main_blueprint
from webapp.auth import auth as auth_blueprint
from webapp.smtp import smtp as smtp_blueprint



if __name__ == '__main__':
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(smtp_blueprint)
    app.run(port=80, debug=True)
