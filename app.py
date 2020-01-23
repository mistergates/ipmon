'''Runs the web server on localhost, port 80'''
from ipmon import app, db, migrate

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=80, use_reloader=True)
