'''User Auth Library'''
import os
import sys

from flask import Blueprint, redirect, url_for, request, flash

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
from ipmon import db, log
from ipmon.database import Users
from ipmon.forms import UpdateEmailForm

auth = Blueprint('auth', __name__)

##########################
# Routes #################
##########################
@auth.route('/updateEmail', methods=['POST'])
def update_email():
    form = UpdateEmailForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            if not form.email.data == form.email_verify.data:
                flash('Email addresses did not match', 'danger')
                return redirect(url_for('main.account'))

            try:
                current_user = Users.query.first()
                current_user.email = form.email.data
                db.session.commit()
                flash('Email successfully updated', 'success')
            except Exception as exc:
                log.error('Failed to update email address: {}'.format(exc))
                flash('Failed to update email address', 'danger')

        else:
            for dummy, errors in form.errors.items():
                for error in errors:
                    flash(error, 'danger')

        return redirect(url_for('main.account'))
