from flask import *
from mysql import mysql

from sister import use_sister
import model

bp=Blueprint('add',__name__)

@bp.route('/add/zone',methods=['POST'])
@use_sister()
def add_zone():
    """
    INPUT:
         names: list of str
    """
    names=request.json['names']

    z_o,_=g.user.zones(need_list=False)
    z_o=z_o.get(None,[])
    if len(z_o)+len(names)>current_app.config['LIMIT_ZONES']:
        flash('课程数量超出限制','error')
        g.action_success=False
        return

    cur=mysql.get_db().cursor()
    z_onew=z_o
    for name in names:
        cur.execute('''
            insert into zones (next_zid, name, uid) values (null, %s, %s)    
        ''',[name,g.user.uid])
        z_onew=z_onew+[cur.lastrowid]

    model.update_linkedlist(z_o,z_onew,'zones')

@bp.route('/add/project',methods=['POST'])
@use_sister()
def add_project():
    """
    INPUT:
        names: list of str
        parent_id: int
    """
    names=request.json['names']
    zid=int(request.json['parent_id'])

    p_o,_=g.user.projects(zid,need_list=False)
    p_o=p_o.get(zid,[])
    if len(p_o)+len(names)>current_app.config['LIMIT_PROJECTS_PER_ZONE']:
        flash('项目数量超出限制','error')
        g.action_success=False
        return

    cur=mysql.get_db().cursor()
    p_onew=p_o
    for name in names:
        cur.execute('''
            insert into projects (next_pid, name, uid, zid) values (null, %s, %s, %s)    
        ''',[name,g.user.uid,zid])
        p_onew=p_onew+[cur.lastrowid]

    model.update_linkedlist(p_o,p_onew,'projects')

@bp.route('/add/task',methods=['POST'])
@use_sister()
def add_task():
    """
    INPUT:
        names: list of str
        parent_id: int
    """
    names=request.json['names']
    pid=int(request.json['parent_id'])

    t_o,_=g.user.tasks(pid,need_list=False)
    t_o=t_o.get(pid,[])
    if len(t_o)+len(names)>current_app.config['LIMIT_TASKS_PER_PROJECT']:
        flash('任务数量超出限制','error')
        g.action_success=False
        return

    cur=mysql.get_db().cursor()
    t_onew=t_o
    for name in names:
        cur.execute('''
            insert into tasks (next_tid, name, uid, pid) values (null, %s, %s, %s)     
        ''',[name,g.user.uid,pid])
        t_onew=t_onew+[cur.lastrowid]

    model.update_linkedlist(t_o,t_onew,'tasks')