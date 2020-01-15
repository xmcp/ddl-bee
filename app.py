from flask import *
from flask_compress import Compress
from mysql import mysql

app=Flask(__name__)
app.config.from_object('config')
mysql.init_app(app)
Compress(app)

import views
from views import *

for module_name in views.__all__:
    app.logger.info('register blueprint %s'%module_name)
    app.register_blueprint(locals()[module_name].bp)

if __name__=='__main__':
    app.run('0.0.0.0',1817)