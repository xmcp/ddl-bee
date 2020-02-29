from flask import *
from mysql import mysql

from sister import use_sister
import random

bp=Blueprint('update',__name__)

def gen_share_hash():
    ALPHABET='qwertyuiopasdfghjkzxcvbnm23456789'
    LENGTH=8
    return ''.join([random.choice(ALPHABET) for _ in range(LENGTH)])

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

    if len(name)>current_app.config['MAX_NAME_LENGTH']:
        flash('名称长度超出限制','error')
        g.action_success=False
        return

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
        shared: bool
    """
    pid=int(request.json['id'])
    name=str(request.json['name'])
    shared=bool(request.json['shared'])

    if shared and g.user.ring>current_app.config['MAX_RING_FOR_SHARING']:
        flash('你所在的用户组不能创建共享','error')
        g.action_success=False
        return

    if len(name)>current_app.config['MAX_NAME_LENGTH']:
        flash('名称长度超出限制','error')
        g.action_success=False
        return

    cur=mysql.get_db().cursor()
    cur.execute('''
        update projects set name=%s where pid=%s and uid=%s
    ''',[name,pid,g.user.uid])

    if shared: # gen share hash if not already shared
        cur.execute('''
            update projects set share_hash=%s where pid=%s and uid=%s and share_hash is null
        ''',[gen_share_hash(),pid,g.user.uid])
    else: # remove share hash
        cur.execute('''
            update projects set share_hash=null where pid=%s and uid=%s
        ''',[pid,g.user.uid])

@bp.route('/update/task',methods=['POST'])
@use_sister()
def update_task():
    """
    INPUT:
        id: int
        name: str
        status: str
        desc: str or null
        due: int or null
    """
    tid=int(request.json['id'])
    name=str(request.json['name'])
    status=str(request.json['status'])
    assert status in ['placeholder','active'], 'invalid status'
    due=request.json['due']
    desc=request.json['desc']

    if due is not None:
        due=int(due)
    if desc is not None:
        desc=str(desc)

    if len(name)>current_app.config['MAX_NAME_LENGTH']:
        flash('名称长度超出限制','error')
        g.action_success=False
        return

    cur=mysql.get_db().cursor()
    cur.execute('''
        update tasks set name=%s, status=%s, due=%s, description=%s where tid=%s and uid=%s
    ''',[name,status,due,desc,tid,g.user.uid])

@bp.route('/update/complete',methods=['POST'])
@use_sister()
def update_complete():
    """
    INPUT:
        ids: list of int
        completeness: str
    """
    tids=request.json['ids']
    completeness=str(request.json['completeness'])
    assert completeness in ['todo','done','highlight','ignored'], 'invalid completeness'

    cur=mysql.get_db().cursor()

    for tid in tids:
        tid=int(tid)

        # set status from placeholder to active, if have permission
        cur.execute('''
            update tasks set status='active' where tid=%s and uid=%s and status='placeholder'
        ''',[tid,g.user.uid])

        if completeness!='todo': # write into completes
            cur.execute('''
                replace into completes (uid, tid, completeness, update_timestamp) values (%s, %s, %s, unix_timestamp()) 
            ''',[g.user.uid,tid,completeness])
        else: # or delte from it
            cur.execute('''
                delete from completes where uid=%s and tid=%s 
            ''',[g.user.uid,tid])
