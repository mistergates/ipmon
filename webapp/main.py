'''Main Web Application'''
import flask_login

from flask import Blueprint, render_template, request

main = Blueprint('main', __name__)

#####################
# App Routes ########
#####################
@main.route('/')
def index():
    '''Index page'''
    return render_template('index.html')


@main.route('/addhosts', methods=['GET', 'POST'])
@flask_login.login_required
def add_hosts():
    '''Add Hosts Page'''
    if request.method == 'GET':
        return render_template('addHosts.html')
    elif request.method == 'POST':
        results = request.form.to_dict()

        print(results)
