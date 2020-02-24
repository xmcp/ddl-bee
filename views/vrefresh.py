from flask import *
from mysql import mysql

from sister import use_sister

bp=Blueprint('refresh',__name__)

@bp.route('/refresh')
@use_sister()
def refresh():
    cur=mysql.get_db().cursor()
    cur.execute('''
        update users set last_refresh=unix_timestamp() where uid=%s
    ''',[g.user.uid])
    # real refresh logic is dealed in model, by sister