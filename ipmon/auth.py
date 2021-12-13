'''User Auth Library'''
import os
import sys

from password_strength import PasswordPolicy
from passlib.hash import sha256_crypt
from flask import Blueprint, render_template, redirect, url_for, request, flash

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
from ipmon import db, config, log
from ipmon.database import Users
from ipmon.schemas import Schemas
from ipmon.forms import UpdateEmailForm
from ipmon.main import database_configured

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


@auth.route('/addUser', methods=['GET', 'POST'])
def add_user():
    '''Add user to database'''
    if request.method == 'GET':
        return render_template('addUser.html')
    elif request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        password_verify = request.form.get('verify_password')
        errors = 0

        if password != password_verify:
            # Verify passwords matched
            flash('Passwords do not match', 'danger')
            errors += 1
        if Users.query.filter_by(username=username).first():
            # Check to see if username exists
            flash('Username already exists', 'danger')
            errors += 1
        if Users.query.filter_by(email=email).first():
            # Check to see if email already exists
            flash('Email address already exists', 'danger')
            errors += 1

        if errors:
            return redirect(url_for('auth.add_user'))

        try:
            # create new user with the form data. Hash the password so plaintext version isn't saved.
            new_user = Users(email=email, username=username, password=sha256_crypt.hash(password))

            # add the new user to the database
            db.session.add(new_user)
            db.session.commit()
            flash('Succussfully added user {}'.format(new_user.username), 'success')
        except Exception:
            flash('Failed to add user', 'danger')

        return redirect(url_for('auth.add_user'))
