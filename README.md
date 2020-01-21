# Bee <small>from _Project Fire Bird_</small>

This is the back-end part of Project Fire Bird

See front-end part at https://github.com/pkuhelper-web/phoenix

## Build Instruction for Self-Hosting

1. Install `python3`, `mysql`, `uwsgi` and maybe `nginx` on your server
2. `python3 -m pip install -r requirements.txt`
3. Create a MySQL database for this backend to use, and set up an account
4. Fill in app configurations in `config.example.py`:
   - `MYSQL_*`: input your database connection credential
   - `SECRET_KEY`: generate a random, secure string
   - `STICKY_MSGS`: notifications that will be shown to all users
5. Implement your token-based account system and registration system in `user_control.example.py`
6. Fill in uWSGI configurations in `wsgi.example.ini`
7. Fill in splash screen configurations in `splashes/__init__.example.py`
8. Rename all example files:
   - `config.example.py` to `config.py`
   - `user_control.example.py` to `user_control.py`
   - `wsgi.example.ini` to `wsgi.ini`
   - `splashes/__init__.example.py` to `splashes/__init__.py`
9. Run `python3 init_db.py` and input `CREATE TABLES`
10. Run `uwsgi --ini wsgi.ini` to start up the backend server
11. Update your web server (maybe `nginx`) configuration to pass API requests to wsgi socket
