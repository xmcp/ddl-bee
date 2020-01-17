from flask import *
from mysql import mysql

from sister import use_sister
import model

bp=Blueprint('reorder',__name__)

def check_same(a,b):
    return len(a)==len(b) and set(a)==set(b)

@bp.route('/reorder/zone',methods=['POST'])
@use_sister()
def reorder_zone():
    """
    INPUT:
        order: list of int
    """
    zids=request.json['order']

    z_o,_=g.user.zones(need_list=False)
    z_o=z_o[None]

    if not check_same(z_o,zids):
        flash('课程发生变化','error')
        g.action_success=False
        return

    model.update_linkedlist(z_o,zids,'zones')

@bp.route('/reorder/project',methods=['POST'])
@use_sister()
def reorder_project():
    """
    INPUT:
        parent_id: int
        order: list of int
    """
    zid=int(request.json['parent_id'])
    pids=request.json['order']

    p_o,_=g.user.projects(zid,need_list=False)
    p_o=p_o[zid]

    if not check_same(p_o,pids):
        flash('项目发生变化','error')
        g.action_success=False
        return

    model.update_linkedlist(p_o,pids,'projects')

@bp.route('/reorder/task',methods=['POST'])
@use_sister()
def reorder_task():
    """
    INPUT:
        parent_id: int
        order: list of int
    """
    pid=int(request.json['parent_id'])
    tids=request.json['order']

    t_o,_=g.user.tasks(pid,need_list=False)
    t_o=t_o[pid]

    if not check_same(t_o,tids):
        flash('任务发生变化','error')
        g.action_success=False
        return

    model.update_linkedlist(t_o,tids,'tasks')