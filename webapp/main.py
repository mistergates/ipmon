'''Main Web Application'''
import os
import sys
import flask_login
import json
import re

from flask import Blueprint, render_template, request, flash, redirect, url_for, send_from_directory

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
from webapp import db, app
from webapp.database import Hosts, Polling, PollHistory, WebThemes, Users, SmtpServer
from webapp.database import HOSTS_SCHEMA, POLLING_SCHEMA, POLL_HISTORY_SCHEMA, WEB_THEMES_SCHEMA, WEB_THEME_SCHEMA, USER_SCHEMA, SMTP_SCHEMA
from webapp.api import get_web_themes, get_polling_config, get_active_theme
from webapp.polling import poll_host, update_poll_scheduler

main = Blueprint('main', __name__)

#####################
# App Routes ########
#####################
@main.route('/favicon.ico')
def favicon():
    '''Favicon'''
    return send_from_directory(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@main.route('/')
def index():
    '''Index page'''
    interval = int(json.loads(get_polling_config())['poll_interval']) * 1000
    return render_template('index.html', poll_interval=interval)


@main.route('/setTheme', methods=['GET', 'POST'])
@flask_login.login_required
def set_theme():
    '''Set Theme'''
    if request.method == 'GET':
        return render_template('setTheme.html', themes=json.loads(get_web_themes()))
    elif request.method == 'POST':
        results = request.form.to_dict()

        try:
            for theme in json.loads(get_web_themes()):
                theme_obj = WebThemes.query.filter_by(id=int(theme['id'])).first()
                if theme_obj.id == int(results['id']):
                    theme_obj.active = True
                else:
                    theme_obj.active = False
            db.session.commit()
            flash('Successfully updated theme', 'success')
        except Exception:
            flash('Failed to update theme', 'danger')
    return redirect(url_for('main.set_theme'))


@main.route('/configurePolling', methods=['GET', 'POST'])
@flask_login.login_required
def configure_polling():
    '''Poll Interval'''
    if request.method == 'GET':
        polling_config = POLLING_SCHEMA.dump(Polling.query.filter_by(id=1).first())
        return render_template('pollingConfig.html', polling_config=polling_config)
    elif request.method == 'POST':
        results = request.form.to_dict()

        polling_config = Polling.query.filter_by(id=1).first()
        try:
            if results['polling_interval']:
                polling_config.poll_interval = int(results['polling_interval'])
            if results['history_truncate_days']:
                polling_config.history_truncate_days = int(results['history_truncate_days'])
            db.session.commit()
        except Exception:
            flash('Failed to update polling interval', 'danger')
            return redirect(url_for('main.configure_polling'))

        # Update scheduled polling interval
        if results['polling_interval']:
            update_poll_scheduler(results['polling_interval'])

        flash('Successfully updated polling interval', 'success')
        return redirect(url_for('main.configure_polling'))


##########################
# Custom Jinja Functions #
##########################
def get_active_theme_path():
    '''Get the file path for the active theme'''
    return json.loads(get_active_theme())['theme_path']
app.add_template_global(get_active_theme_path, name='get_active_theme_path')
