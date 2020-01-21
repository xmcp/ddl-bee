from flask import *
from mysql import mysql

from sister import use_sister
import model

bp=Blueprint('delete',__name__)

@bp.route('/delete/zone',methods=['POST'])
@use_sister()
def delete_zone():
    """
    INPUT:
        id: int
    """
    zid=int(request.json['id'])

    z_o,_=g.user.zones(need_list=False)
    z_o=z_o.get(None,[])
    if zid not in z_o:
        flash('课程不存在或没有权限','error')
        g.action_success=False
        return

    cur=mysql.get_db().cursor()
    cur.execute('''
        delete from zones where zid=%s and uid=%s
    ''',[zid,g.user.uid])

    z_onew=z_o[:]
    z_onew.remove(zid)
    model.update_linkedlist(z_o,z_onew,'zones')

@bp.route('/delete/project',methods=['POST'])
@use_sister()
def delete_project():
    """
    INPUT:
        id: int
        parent_id: int
    """
    pid=int(request.json['id'])
    zid=int(request.json['parent_id'])

    p_o,_=g.user.projects(zid,need_list=False)
    p_o=p_o.get(zid,[])
    if pid not in p_o:
        flash('类别不存在或没有权限','error')
        g.action_success=False
        return

    cur=mysql.get_db().cursor()

    # get linked extpid
    cur.execute('''
        select extpid from projects where pid=%s
    ''',[pid])
    extpid=cur.fetchone()[0]

    if extpid is None: # src project
        cur.execute('''
            select count(*) from projects where extpid=%s
        ''',[pid])
        peercnt=cur.fetchone()[0]

        if peercnt==0: # no peers: safely delete
            cur.execute('''
                delete from projects where pid=%s and uid=%s
            ''',[pid,g.user.uid])

        else: # otherwise: only remove from current user, delete it later
            cur.execute('''
                update projects set uid=null, zid=null where pid=%s and uid=%s
            ''',[pid,g.user.uid])
            cur.execute('''
                update tasks set uid=null where pid=%s and uid=%s
            ''',[pid,g.user.uid])
            # completes will be deleted after last person deletes the project and tasks are deleted

    else: # imported project
        # delete self
        cur.execute('''
            delete from projects where pid=%s and uid=%s
        ''',[pid,g.user.uid])

        cur.execute('''
            select count(*) from projects where
                (extpid=%s and pid!=%s) or /* other imported ones */
                (pid=%s and uid is not null) /* original one that is not flagged as deletion */
        ''',[extpid,pid,extpid])
        peercnt=cur.fetchone()[0]

        if peercnt==0: # delete src
            cur.execute('''
                delete from projects where pid=%s
            ''',[extpid])

    p_onew=p_o[:]
    p_onew.remove(pid)
    model.update_linkedlist(p_o,p_onew,'projects')

@bp.route('/delete/task',methods=['POST'])
@use_sister()
def delete_task():
    """
    INPUT:
        id: int
        parent_id: int
    """
    tid=int(request.json['id'])
    pid=int(request.json['parent_id'])

    t_o,_=g.user.tasks(pid,need_list=False)
    t_o=t_o.get(pid,[])
    if tid not in t_o:
        flash('任务不存在或没有权限','error')
        g.action_success=False
        return

    cur=mysql.get_db().cursor()
    cur.execute('''
        delete from tasks where tid=%s and uid=%s
    ''',[tid,g.user.uid])

    t_onew=t_o[:]
    t_onew.remove(tid)
    model.update_linkedlist(t_o,t_onew,'tasks')