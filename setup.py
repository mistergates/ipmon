'''Setup File Script

This file should be run to create and configure the database.
If the database already exists, this script will exit.
'''
import os
import sys
import getpass
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')

try:
    from passlib.hash import sha256_crypt
    from sqlalchemy import create_engine

    from webapp import db, config, app
    from webapp.database import Users
except ImportError:
    print('\nFailed to load required modules. Try running "pip install -r {}" from command line.\n'.format(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'requirements.txt')))
    sys.exit(1)

def check_existing_database():
    '''Checks to see if the database already exists. Exit if it does.'''
    database_file = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        config['Database_Name']
    )
    if os.path.exists(database_file):
        print('Database file "{}" already exists.'.format(database_file))
        print('To reconfigure the database, please delete this file first.')
        print('\nWARNING: Deleting this file WILL DESTROY ALL DATA (Users, currency, etc.). DELETE AT YOUR OWN RISK!')
        print('\n\nExiting setup...')
        sys.exit(1)


def create_database():
    '''Creates the database with defined tables'''
    print('Creating the database and tables...')
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], echo=True)
    db.Model.metadata.create_all(engine)


def create_admin_user_interactive():
    '''Create the admin user interactively'''
    print('Creating the admin user account...')
    while True:
        username = input('  Username: ').strip()
        email = input('  Email Address: ').strip()
        if 'y' in input('\n  Continue with the above information? [Y/n] ').strip().lower():
            break

    while True:
        password = getpass.getpass(prompt='\n  Password: ').strip()
        verify = getpass.getpass(prompt='  Re-enter Password: ').strip()

        if password == verify:
            break
        else:
            print('\n!! Passwords did not match !!\n')

    with app.app_context():
        admin_user = Users(email=email, username=username, password=sha256_crypt.hash(password))
        db.session.add(admin_user)
        db.session.commit()



def failure_cleanup(error):
    '''If we encountered a failure, delete the database and inform the user'''
    print('\n\n!! Encountered an error during setup:\n{}\n\nAborting !!'.format(error))
    database_file = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        config['Database_Name']
    )

    print('  Removing database file "{}"'.format(database_file))
    os.remove(database_file)


if __name__ == '__main__':
    try:
        check_existing_database()
        create_database()
        create_admin_user_interactive()
    except (Exception, KeyboardInterrupt) as exc:
        failure_cleanup(exc)
        sys.exit(1)

    print('\n\nSetup complete!')
    print('To start the webapp, please run "python webapp/webserv.py" (lazy loading, move to a service for production use)\n')
