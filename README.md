![preview](https://i.imgur.com/LjrrYNk.png)

Monitor IP addresses by polling them via ICMP (ping) requests.

A web app is made available using Flask to view IP address statuses and poll history.

Polling runs as a service as part of the web app.

A SQLite DB is used for storing hosts, polling results, user accounts, etc.



# Setup
The following setups will need to be performed in order for setup:

## 1) Install Python
Python 3.0+ needs to be installed, you can find installers [here](https://www.python.org/downloads/)


## 2) Install Python Requirements
From the main directory of this repo, run the following command:

```
pip install -r requirements.txt
```

## 3) Run Setup
From the main directory of this repo, run the following command and follow the interactive setup:

```
python setup.py
```

***Note:*** You will configure an admin account during setup, this account will need to be used for full functionality. By default, unauthenticated visitors will only be able to view IP statuses.

# Running Web Server
To run the web server the most basic (lazy) way, you can run the following from the main directory of this repo:
```
python webserv.py
```

There are some configurable arguments, to view those simply run:
```
python webserv.py -h
```

By default, the web server will be running on ***http://127.0.0.1:80***

***Note:*** It would be wise to move this to a WSGI server for production use, see [here](https://flask.palletsprojects.com/en/1.1.x/deploying/)

# TODO
- Configure job to truncate poll logs (user controls how long to keep logs)
- Move forms to WTForms w/ validations
- Move javascript to static file
- Account page
    - Notifications Toggle
    - Update Password
    - Update Email
- Add/Update/Remove users under Configuration menu
- Keep track of database schema changes
- Correctly join tables
- Document APIs