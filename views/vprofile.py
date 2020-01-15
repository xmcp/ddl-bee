from flask import *
from mysql import mysql

from sister import use_sister, SisterErrorMsg
import model
import splashes
import user_control

bp=Blueprint('profile',__name__)

@bp.route('/profile/register')
@use_sister(enforce_auth=False,enforce_splash=False)
def register():
    """
    ARGS:
        user_token -> g.token as dealed in sister
    INPUT:
        regcode: str
    """
    if not g.token:
        raise SisterErrorMsg('未登录')
    regcode=str(request.json['regcode'])

    cur=mysql.get_db().cursor()

    info=user_control.get_info_from_user_token(g.token)
    if info is None:
        raise SisterErrorMsg('用户不存在')

    unique_id=info['unique_id']
    cur.execute('''
        select count(*) from users where unique_id=%s
    ''',[unique_id])

    if cur.fetchone()[0]>0: # already registered: update user token
        cur.execute('''
            update users set user_token=%s where unique_id=%s
        ''',[g.token,unique_id])

        flash('%s，欢迎回来'%info['name'],'message')

    else: # register new one
        reg=user_control.check_registration_code(regcode,info)
        if reg['error'] is not None:
            raise SisterErrorMsg(reg['error'])

        cur.execute('''
            insert into users (user_token, unique_id, name, ring, splash_index, remarks, settings)
            values (%s, %s, %s, %s, %s, %s, '{}')
        ''',[g.token,unique_id,info['name'],reg['ring'],reg['splash_index'],info['remarks']+reg['remarks']])

        flash('注册成功','message')

@bp.route('/profile/splash_callback')
@use_sister(enforce_splash=False)
def splash_callback():
    """
    INPUT:
        splash_index: int
        handin: any jsonable item that will be passed to splash handler
    """
    splash_index=int(request.json['splash_index'])
    handin_data=request.json['handin']

    assert g.user.splash_index==splash_index, 'not in current splash'
    handler=splashes.SplashHandler.get_handler_by_index(splash_index)
    assert handler is not None, 'no handler for this splash'
    return handler.handin(g.user.uid,handin_data)