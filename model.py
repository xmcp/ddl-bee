import functools
import json
from flask import *
from mysql import mysql

def sort_linkedlist(ll,fn_recover,*,idx_id,idx_next,idx_group,attrs):
    """ Parse a linked list into sorted list.

    :param ll: [[table_cell...], ...] input linked list
    :param fn_recover: function(group_val, {id: item, ...})->None to be called when linked list is corrupted. after that order is undefined
    :param idx_id: column index for id in input
    :param idx_next: column index for next id ptr in input
    :param idx_group: column index for group in input, None for not groupped
    :param attrs: [name...] name for each column in input cell, name=None for ignored column, attrs=None will return items=None

    :return: (order_in_each_group, items); order_in_each_group={group_val: [ids...], ...}; items={id: {key: val, ...}, ...} or None
    """

    ll_grouped={} # {group_val: {id: item, ...}, ...}
    for item in ll:
        ll_grouped.setdefault(None if idx_group is None else item[idx_group],{})[item[idx_id]]=item

    ret_order={}
    for group_val,ll_dict in ll_grouped.items(): # each group
        try:
            # get first item
            first_item_candidates=set(ll_dict.keys())
            for item in ll_dict.values():
                if item[idx_next] is not None:
                    first_item_candidates.remove(item[idx_next])
            assert len(first_item_candidates)==1, '%d first candidates'%len(first_item_candidates)

            # get whole list
            nxt_key=next(iter(first_item_candidates)) # its only item
            sorted_ids=[]
            for _ in range(len(ll_dict)):
                nxt_item=ll_dict[nxt_key]
                sorted_ids.append(nxt_key)
                nxt_key=nxt_item[idx_next]
            assert nxt_key is None, 'got trailing next key %s'%nxt_key
        except Exception as e:
            current_app.logger.exception('linked list failure in group %s'%group_val)
            flash('linked list failure in group %s: %s %s'%(group_val,type(e),e),'error')
            fn_recover(group_val,ll_dict)
            sorted_ids=list(ll_dict.keys())

        ret_order[group_val]=sorted_ids

    def get_attr_dict(item):
        return {key:val for key,val in zip(attrs,item) if key is not None}

    # transform to output format
    ret_items=None if attrs is None else {item[idx_id]:get_attr_dict(item) for item in ll}

    return ret_order, ret_items

def update_linkedlist(before,after,table_name):
    """ Modify linked list and write to database.
    :param before: [id...] original linked list status to reduce writes, None for unknown
    :param after: [id...] new linked list status which will write to db
    :param table_name: table name, in ['zones','projects','tasks']
    """
    key_name={'zones':'zid','projects':'pid','tasks':'tid'}.get(table_name,None)
    if key_name is None:
        raise ValueError('update_linkedlist table_name is %r'%table_name)

    cur=mysql.get_db().cursor()
    # noinspection SqlWithoutWhere
    sql='update %s set next_%s=%%s where %s=%%s and uid=%%s'%(table_name,key_name,key_name)

    before=([] if before is None else before)+[None]
    after=list(after)+[None]

    before_nxts={before[i]:before[i+1] for i in range(len(before)-1)}
    chgs=[]
    for i in range(len(after)-1):
        if after[i+1]!=before_nxts.get(after[i],...):
            chgs.append([after[i+1],after[i],g.user.uid])
    if chgs:
        cur.executemany(sql,chgs)

class User:
    def __init__(self,uid,name,ring,splash_index,settings):
        self.uid=uid
        assert isinstance(self.uid,int), 'uid not integer: %r'%self.uid
        self.name=name
        self.ring=ring
        self.splash_index=splash_index
        try:
            self.settings=json.loads(settings)
        except Exception as e:
            current_app.logger.exception('unserialize settings %r for user %d',settings,self.uid)
            flash('user settings %r unserialize failed for user %d: %s %s'%(settings,self.uid,type(e),e),'error')
            cur=mysql.get_db().cursor()
            cur.execute('''
                update users set settings='{}' where uid=%s
            ''',[self.uid])
            self.settings={}


    def user_info(self):
        """ Generate info under `user` key that will be passwd to phoenix.
        :return: a dict
        """
        return {
            'name': self.name,
            'ring': self.ring,
            'splash_index': self.splash_index,
            'settings': self.settings,
        }

    def zones(self,*,need_list=True):
        """ Get zones and their ordering.
        :param need_list: False if second ret val is unnecessary (will return None)
        :return: {None: [zid, ...]}, {zid: {'name','id'}, ...}
        """
        cur=mysql.get_db().cursor()
        cur.execute('''
            select zid,next_zid,name from zones where uid=%s
        ''',[self.uid])

        def recover(_group,ll_dict):
            update_linkedlist(None,ll_dict.keys(),'zones')

        return sort_linkedlist(cur.fetchall(),recover,
            idx_id=0,
            idx_next=1,
            idx_group=None,
            attrs=['id',None,'name'] if need_list else None,
        )

    def projects(self,zid=None,*,need_list=True):
        """ Get projects and their ordering.
        :param zid: specify zone id to retrive, None to retrive all
        :param need_list: False if second ret val is unnecessary (will return None)
        :return: {zid: [pid, ...]}, {pid: {'name','id',...}, ...}
        """
        cur=mysql.get_db().cursor()
        sql='''
            select pid,next_pid,zid,name,extpid,share_hash from projects where uid=%s
        '''

        if zid is None:
            cur.execute(sql,[self.uid])
        else:
            cur.execute(sql+' and zid=%s',[self.uid,zid])

        def recover(_group,ll_dict):
            update_linkedlist(None,ll_dict.keys(),'projects')

        return sort_linkedlist(cur.fetchall(),recover,
            idx_id=0,
            idx_next=1,
            idx_group=2,
            attrs=['id',None,'parent_id','name','_extpid','share_hash'] if need_list else None,
        )

    def tasks(self,pid=None,*,need_list=True,bypass_permission=False):
        """ Get tasks and their ordering.
        :param pid: int or list (for multiple). specify project id to retrive, None to retrive all
        :param need_list: False if second ret val is unnecessary (will return None)
        :param bypass_permission: use with `pid`. set to True to remove limit of only fetching tasks of current user
        :return: {pid: [tid, ...]}, {tid: {'name','id','status','due'...}, ...}
        """
        cur=mysql.get_db().cursor()
        sql='''
            select tasks.tid,next_tid,pid,name,status,due,ifnull(completeness,'todo'),completes.update_timestamp,description from tasks
            left join completes on tasks.tid=completes.tid and completes.uid=%s
            where 1 
        '''
        sql_args=[g.user.uid]

        if bypass_permission and pid is None:
            raise ValueError('bypassing permission without pid')

        if pid is not None:
            if isinstance(pid,list):
                if not pid:
                    return {}, {}
                sql+=' and tasks.pid in %s'
                sql_args.append(pid)
            else:
                sql+=' and tasks.pid=%s'
                sql_args.append(pid)

        if not bypass_permission:
            sql+=' and tasks.uid=%s'
            sql_args.append(self.uid)

        cur.execute(sql,sql_args)

        def recover(_group,ll_dict):
            update_linkedlist(None,ll_dict.keys(),'tasks')

        return sort_linkedlist(cur.fetchall(),recover,
            idx_id=0,
            idx_next=1,
            idx_group=2,
            attrs=['id',None,'parent_id','name','status','due','completeness','complete_timestamp','desc'] if need_list else None,
        )

    def tasks_external(self,pid_map):
        """ Get external tasks and their ordering.
        :param pid_map: {original_pid: external_pid, ...}
        :return: {original_pid: [tid, ...]}, {tid: {'name','id',...}, ...}
        """
        ret_o={}
        ret_li={}
        rev_pid_map={v:k for k,v in pid_map.items()}

        t_o,t_li=self.tasks(list(pid_map.values()),bypass_permission=True)

        for orig_pid,ext_pid in pid_map.items():
            ret_o[orig_pid]=t_o.get(ext_pid,[])

        for tid,item in t_li.items():
            item['parent_id']=rev_pid_map[item['parent_id']]
            ret_li[tid]=item

        return ret_o,ret_li

    @functools.lru_cache(1024)
    def check_zone(self,zid):
        """ Check whether the user have control of the given zid.
        :param zid: int
        :return: bool
        """
        cur=mysql.get_db().cursor()
        cur.execute('''
            select count(*) from zones where zid=%s and uid=%s
        ''',[zid,self.uid])
        return cur.fetchone()[0]!=0

    @functools.lru_cache(1024)
    def check_project(self,pid):
        """ Check whether the user have control of the given pid.
        :param pid: int
        :return: bool
        """
        cur=mysql.get_db().cursor()
        cur.execute('''
            select count(*) from projects where pid=%s and uid=%s
        ''',[pid,self.uid])
        return cur.fetchone()[0]!=0

    def imported_extpids(self):
        """ Return list of extpids that the user has already imported.
        :return: list of extpids
        """
        cur=mysql.get_db().cursor()
        cur.execute('''
            select extpid from projects where uid=%s and extpid is not null
        ''',[self.uid])
        return [x[0] for x in cur.fetchall()]

    def build_sister_response(self):
        """ Generate value that will be passed to phoenix.
        :return: a dict
        """
        z_o,z_li=self.zones()
        p_o,p_li=self.projects()
        t_o,t_li=self.tasks()

        ext_projs={pid:item['_extpid'] for pid,item in p_li.items() if item['_extpid']}
        tex_o,tex_li=self.tasks_external(ext_projs)
        t_o.update(tex_o)
        t_li.update(tex_li)

        return {
            'zone_order': z_o.get(None,[]),

            'zone': {zid: {
                'project_order': p_o.get(zid,[]),
                **item,
            } for zid,item in z_li.items()},

            'project': {pid: {
                'task_order':t_o.get(pid,[]),
                'external': item['_extpid'] is not None,
                **{k:v for k,v in item.items() if not k.startswith('_')},
            } for pid,item in p_li.items()},

            'task': t_li,
        }