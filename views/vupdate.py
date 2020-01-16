from flask import *
from mysql import mysql

from sister import use_sister
import model

bp=Blueprint('update',__name__)

@bp.route('/update/zone',methods=['POST'])
@use_sister()
def update_zone():
    """
    INPUT:
        id: int
        name: str
    """
    zid=int(request.json['id'])
    name=str(request.json['name'])

    cur=mysql.get_db().cursor()
    cur.execute('''
        update zones set name=%s where zid=%s and uid=%s
    ''',[name,zid,g.user.uid])

@bp.route('/update/project',methods=['POST'])
@use_sister()
def update_project():
    """
    INPUT:
        id: int
        name: str
    """
    pid=int(request.json['id'])
    name=str(request.json['name'])

    cur=mysql.get_db().cursor()
    cur.execute('''
        update projects set name=%s where pid=%s and uid=%s
    ''',[name,pid,g.user.uid])

@bp.route('/update/task',methods=['POST'])
@use_sister()
def update_task():
    """
    INPUT:
        id: int
        name: str
        status: str
        due: int or null
    """
    tid=int(request.json['id'])
    name=str(request.json['name'])
    status=str(request.json['status'])
    assert status in ['placeholder','active'], 'invalid status'
    due=request.json['due']
    if due is not None:
        due=int(due)

    cur=mysql.get_db().cursor()
    cur.execute('''
        update tasks set name=%s, status=%s, due=%s where tid=%s and uid=%s
    ''',[name,status,due,tid,g.user.uid])

@bp.route('/update/complete',methods=['POST'])
@use_sister()
def update_complete():
    """
    INPUT:
        id: int
        completeness: str
    """
    tid=int(request.json['id'])
    completeness=str(request.json['completeness'])
    assert completeness in ['todo','done','highlight','ignored'], 'invalid completeness'

    cur=mysql.get_db().cursor()
    cur.execute('''
        replace into completes (uid, tid, completeness) values (%s, %s, %s) 
    ''',[g.user.uid,tid,completeness])

@bp.route('/update/task_direct_done',methods=['POST'])
@use_sister()
def update_task_direct_done():
    """
    INPUT:
        id: int
    """
    tid=int(request.json['id'])

    cur=mysql.get_db().cursor()
    cur.execute('''
        update tasks set status='active', due=null where tid=%s and uid=%s
    ''',[tid,g.user.uid])
    cur.execute('''
        replace into completes (uid, tid, completeness) values (%s, %s, 'done') 
    ''',[g.user.uid,tid])