'''User Auth Library'''
import os
import sys
import re
import flask_login

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
from webapp import login_manager
from webapp import db
from webapp.database import Users, USER_SCHEMA

from passlib.hash import sha256_crypt
from flask import Blueprint, render_template, redirect, url_for, request, flash

auth = Blueprint('auth', __name__)


##########################
# Database calls #########
##########################
def get_user(username):
    """Get user based on username. Will try to find user via email if email address was provided.

    Args:
        username (str): Username

    Returns:
        dict
    """
    regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
    if re.search(regex, str(username)):
        user_data = Users.query.filter_by(email=username).first()
    else:
        user_data = Users.query.filter_by(username=username).first()
    return USER_SCHEMA.dump(user_data)


def verify_password(form):
    """Verify password entered using SHA256 Encryption.

    Args:
        form (dict): A dictionary of form info

    Returns:
        bool: Whether or not the password was verified.
    """
    return sha256_crypt.verify(form['password'], get_user(form['username'])['password'])


##########################
# Routes #################
##########################
@auth.route("/account")
@flask_login.login_required
def account():
    '''User Account'''
    return render_template('account.html')


@auth.route("/logout")
@flask_login.login_required
def logout():
    '''Logout user'''
    flask_login.logout_user()
    # return redirect(request.referrer)
    return redirect(url_for('main.index'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    '''Login page'''
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form['username']
    remember = True if request.form.get('remember') else False

    if not get_user(username) or not verify_password(request.form):
        flash('Invalid Username/Password')
    elif verify_password(request.form):
        user = User()
        user.id = username
        flask_login.login_user(user, remember=remember)
        return redirect(url_for('main.index'))
    else:
        flash('Error logging in')

    return redirect(url_for('auth.login'))


@auth.route('/addUser', methods=['GET', 'POST'])
@flask_login.login_required
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


##########################
# Login Manager ##########
##########################
class User(flask_login.UserMixin):
    '''User object'''


@login_manager.user_loader
def user_loader(username):
    '''Load user'''
    if not get_user(username):
        return

    user = User()
    user.id = username
    return user


@login_manager.request_loader
def request_loader(req):
    '''Login request'''
    username = req.form.get('username')
    password = req.form.get('password')

    if not get_user(username):
        # Username not found
        return

    if not verify_password( {'username': username, 'password': password} ):
        # Invalid password provided
        return

    user = User()
    user.id = username

    return user
