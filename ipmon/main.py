'''Main Web Application'''
import os
import sys
import json
import atexit

import flask_login
from flask import Blueprint, render_template, request, flash, redirect, url_for, send_from_directory
from werkzeug.exceptions import HTTPException

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
from ipmon import db, app, scheduler, config
from ipmon.api import get_web_themes, get_polling_config, get_active_theme
from ipmon.database import Polling, WebThemes
from ipmon.forms import PollingConfigForm, UpdatePasswordForm, UpdateEmailForm
from ipmon.polling import update_poll_scheduler, add_poll_history_cleanup_cron
from ipmon.alerts import update_host_status_alert_schedule
from wtforms.validators import NumberRange

main = Blueprint('main', __name__)

#####################
# Schedule Jobs #####
#####################
@app.before_first_request
def webapp_init():
    # Register error handling
    for cls in HTTPException.__subclasses__():
        app.register_error_handler(cls, handle_error)

    if not database_configured():
        return

    init_schedulers()


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
    if not os.path.exists(config['Database_Path']):
        return redirect(url_for('setup.setup'))
    return render_template('index.html', refresh_interval=10000)


@main.route("/account")
@flask_login.login_required
def account():
    '''User Account'''
    password_form = UpdatePasswordForm()
    email_form = UpdateEmailForm()
    return render_template('account.html', password_form=password_form, email_form=email_form)


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
    form = PollingConfigForm()
    if request.method == 'GET':
        polling_config = json.loads(get_polling_config())
        return render_template('pollingConfig.html', polling_config=polling_config, form=form)
    elif request.method == 'POST':
        if form.validate_on_submit():

            polling_config = Polling.query.first()
            try:
                if form.interval.data:
                    polling_config.poll_interval = int(form.interval.data)
                if form.retention_days.data:
                    polling_config.history_truncate_days = int(form.retention_days.data)
                db.session.commit()
            except Exception:
                flash('Failed to update polling interval', 'danger')
                return redirect(url_for('main.configure_polling'))

            # Update scheduled polling interval
            if form.interval.data:
                update_poll_scheduler(form.interval.data)

            flash('Successfully updated polling interval', 'success')
        else:
            for dummy, errors in form.errors.items():
                for error in errors:
                    flash(error, 'danger')

        return redirect(url_for('main.configure_polling'))


##########################
# Functions ##############
##########################
def handle_error(error):
    '''Global Error Handler'''
    code = 500
    desc = 'Internal Server Error'
    if isinstance(error, HTTPException):
        code = error.code
        desc = error.description
    return render_template('error.html', code=code, desc=desc)


def init_schedulers():
    # Register scheduler jobs
    update_poll_scheduler(int(json.loads(get_polling_config())['poll_interval']))
    update_host_status_alert_schedule(int(json.loads(get_polling_config())['poll_interval']) / 2)
    add_poll_history_cleanup_cron()
    atexit.register(scheduler.shutdown)


##########################
# Custom Jinja Functions #
##########################
def get_active_theme_path():
    '''Get the file path for the active theme'''
    if not database_configured():
        return '/static/css/darkly.min.css'
    return json.loads(get_active_theme())['theme_path']
app.add_template_global(get_active_theme_path, name='get_active_theme_path')


def database_configured():
    '''Checks to see if database is configured'''
    return os.path.exists(config['Database_Path'])
app.add_template_global(database_configured, name='database_configured')
