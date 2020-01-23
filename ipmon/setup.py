'''Setup Web App'''
import os
import sys

from flask import Blueprint, render_template, request, flash, redirect, url_for
from sqlalchemy import create_engine
from passlib.hash import sha256_crypt

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
from ipmon import db, config, app
from ipmon.database import Users, Polling, SmtpServer, WebThemes
from ipmon.forms import FirstTimeSetupForm
from ipmon.main import init_schedulers, database_configured
from ipmon.auth import test_password

bp = Blueprint('setup', __name__)

@bp.route('/setup', methods=['GET', 'POST'])
def setup():
    form = FirstTimeSetupForm()
    if request.method == 'GET':
        if database_configured():
            return redirect(url_for('main.index'))
        return render_template('setup.html', form=form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            errors = 0
            if form.password.data != form.verify_password.data:
                flash('Passwords did not match', '')
                errors += 1

            if test_password(form.password.data):
                reqs = form.password.description
                flash('Password did not meet {}'.format(reqs), 'danger')
                errors += 1

            if errors:
                return redirect(url_for('setup.setup'))

        else:
            for dummy, errors in form.errors.items():
                for error in errors:
                    flash(error, 'danger')
            return redirect(url_for('setup.setup'))

        # Create database
        database_file = app.config['SQLALCHEMY_DATABASE_URI']
        database_directory = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'database'
        )
        if not os.path.exists(database_directory):
            os.makedirs(database_directory)
        engine = create_engine(database_file, echo=True)
        db.Model.metadata.create_all(engine)

        # Create admin user
        admin_user = Users(email=form.email.data, username=form.username.data, password=sha256_crypt.hash(form.password.data))
        db.session.add(admin_user)

        # Set polling interval
        poll = Polling(poll_interval=form.poll_interval.data, history_truncate_days=form.retention_days.data)
        db.session.add(poll)

        # Setup STMP server
        smtp = SmtpServer(smtp_server=form.smtp_server.data, smtp_port=form.smtp_port.data, smtp_sender=form.smtp_sender.data)
        db.session.add(smtp)

        # Add web themes
        for i, theme in enumerate(config['Web_Themes']):
            active = False
            if i == 0:
                active = True
            web_theme = WebThemes(theme_name=theme, theme_path=config['Web_Themes'][theme], active=active)
            db.session.add(web_theme)


        # Commit DB updates
        db.session.commit()

        # Initialize schedulers
        init_schedulers()

        return redirect(url_for('main.index'))
