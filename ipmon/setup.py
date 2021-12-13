'''Setup Web App'''
import os
import sys

from flask import Blueprint, render_template, request, flash, redirect, url_for
from sqlalchemy import create_engine

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
from ipmon import db, config, app
from ipmon.database import Users, Polling, SmtpServer, WebThemes
from ipmon.forms import FirstTimeSetupForm
from ipmon.main import init_schedulers, database_configured

bp = Blueprint('setup', __name__)

@bp.route('/setup', methods=['GET', 'POST'])
def setup():
    form = FirstTimeSetupForm()
    if request.method == 'GET':
        if database_configured():
            return redirect(url_for('main.index'))
        return render_template('setup.html', form=form)
    elif request.method == 'POST':
        if not form.validate_on_submit():
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
        user = Users(email=form.email.data)
        db.session.add(user)

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
