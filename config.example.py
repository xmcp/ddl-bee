MYSQL_DATABASE_HOST='127.0.0.1'
MYSQL_DATABASE_USER='user'
MYSQL_DATABASE_PASSWORD='password'
MYSQL_DATABASE_DB='db'

DEBUG=True
COMPRESS_LEVEL=9
JSONIFY_PRETTYPRINT_REGULAR=False

SECRET_KEY=b'42'

MAX_NAME_LENGTH=70 # max allowed length for task & project & zone names, should be less than varchar(_) in db

LIMIT_ZONES=100
LIMIT_PROJECTS_PER_ZONE=100
LIMIT_TASKS_PER_PROJECT=100

INITIAL_SPLASH_INDEX=0
SETTINGS_MAX_BYTES=4096

MAX_RING_FOR_SHARING=3

STICKY_MSGS=[
    ['message','<b>这是公告</b>']
]