from flask import *
from mysql import mysql

from sister import use_sister
import random

bp=Blueprint('update',__name__)

def gen_share_hash():
    ALPHABET='qwertyuiopasdfghjkzxcvbnm23456789'
    LENGTH=8
    return ''.join([random.choice(ALPHABET) for _ in range(LENGTH)])

def str_prefix_length(a,b):
    l=min(len(a),len(b))
    for i in range(l):
        if a[i]!=b[i]:
            return i
    return l

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
        share_name: str
    """
    pid=int(request.json['id'])
    name=str(request.json['name'])
    shared=bool(request.json['shared'])
    share_name=request.json['share_name']
    if share_name is not None:
        share_name=str(share_name)

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

    if shared:
        # gen share hash if not already shared
        cur.execute('''
            update projects set share_hash=%s where pid=%s and uid=%s and extpid is null and share_hash is null
        ''',[gen_share_hash(),pid,g.user.uid])
        # update share name
        cur.execute('''
            update projects set share_name=%s where pid=%s and uid=%s and extpid is null
        ''',[share_name,pid,g.user.uid])
    else:
        # clear share hash and share name
        cur.execute('''
            update projects set share_hash=null, share_name=null where pid=%s and uid=%s
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
        select description from tasks where tid=%s and uid=%s
    ''',[tid,g.user.uid])
    res=cur.fetchone()
    if not res:
        flash('任务不存在或没有权限','error')
        g.action_success=False
        return

    prefix_len=str_prefix_length(res[0] or '',desc or '')
    if prefix_len<len(res[0] or ''): # prefix gets shorter, so need to remove affected desc idx
        cur.execute('''
            update completes set description_idx=%s where tid=%s and description_idx>%s
        ''',[prefix_len,tid,prefix_len])

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
    tids=list(request.json['ids'])
    completeness=str(request.json['completeness'])
    assert completeness in ['todo','done','highlight','ignored'], 'invalid completeness'

    if len(tids)>current_app.config['LIMIT_TASKS_PER_PROJECT']:
        flash('任务数量超出限制','error')
        g.action_success=False
        return

    cur=mysql.get_db().cursor()

    for tid in tids:
        tid=int(tid)

        # set status from placeholder to active, if have permission
        cur.execute('''
            update tasks set status='active' where tid=%s and uid=%s and status='placeholder'
        ''',[tid,g.user.uid])

        # keeping description_idx same
        cur.execute('''
            insert into completes (uid, tid, completeness, update_timestamp) values (%s, %s, %s, unix_timestamp())
            on duplicate key update completeness=%s, update_timestamp=unix_timestamp()
        ''',[g.user.uid,tid,completeness,completeness])

@bp.route('/update/desc_idx',methods=['POST'])
@use_sister()
def update_desc_idx():
    """
    INPUT:
        id: int
        desc_idx: int or null
    """
    tid=int(request.json['id'])
    desc_idx=request.json['desc_idx']
    if desc_idx is not None:
        desc_idx=int(desc_idx)

    cur=mysql.get_db().cursor()

    # keeping completeness same
    cur.execute('''
        insert into completes (uid, tid, completeness, update_timestamp, description_idx) values (%s, %s, 'todo', unix_timestamp(), %s)
        on duplicate key update description_idx=%s
    ''',[g.user.uid,tid,desc_idx,desc_idx])
