from flask import *
from mysql import mysql
import json

from sister import use_sister,SisterErrorMsg,SisterProceed
import splashes
import user_control

bp=Blueprint('profile',__name__)

@bp.route('/profile/register',methods=['POST'])
@use_sister(require_ring=None,enforce_splash=False)
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

    try:
        info=user_control.get_info_from_user_token(g.token)
    except Exception as e:
        current_app.logger.exception('get info from user token failed')
        raise SisterErrorMsg('查询用户信息失败')

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

        flash('%s，欢迎回来'%info['name'],'success')

    else: # register new one
        try:
            reg=user_control.check_registration_code(regcode,info)
        except Exception as e:
            current_app.logger.exception('check registration code failed')
            raise SisterErrorMsg('检查注册条件失败')

        if reg['error'] is not None:
            raise SisterErrorMsg(reg['error'])

        if reg['splash_index'] is None:
            reg['splash_index']=current_app.config['INITIAL_SPLASH_INDEX']

        cur.execute('''
            insert into users (user_token, unique_id, name, ring, splash_index, remarks, settings)
            values (%s, %s, %s, %s, %s, %s, '{}')
        ''',[g.token,unique_id,info['name'],reg['ring'],reg['splash_index'],reg['remarks']])

        flash('注册成功','success')

    raise SisterProceed()

@bp.route('/profile/splash_callback',methods=['POST'])
@use_sister(enforce_splash=False)
def splash_callback():
    """
    INPUT:
        splash_index: int
        handin: any jsonable item that will be passed to splash handler
    """
    splash_index=int(request.json['splash_index'])
    handin_data=request.json['handin']

    if g.user.splash_index!=splash_index:
        raise SisterErrorMsg('not in current splash screen')
    handler=splashes.SplashHandler.get_handler_by_index(splash_index)
    assert handler is not None, 'no handler for this splash'

    handler.handin(g.user.uid,handin_data)
    raise SisterProceed()

@bp.route('/profile/update_settings',methods=['POST'])
@use_sister()
def update_settings():
    """
    IPNUT:
        settings: json object
    """
    settings_obj=request.json['settings']
    settings_str=json.dumps(settings_obj)

    if len(settings_str)>current_app.config['SETTINGS_MAX_BYTES']:
        flash('设置大小超过限制','error')
        g.action_success=False
        return

    cur=mysql.get_db().cursor()
    cur.execute('''
        update users set settings=%s where uid=%s
    ''',[settings_str,g.user.uid])
    raise SisterProceed()

@bp.route('/profile/reset_splash_index',methods=['POST'])
@use_sister()
def reset_splash_index():
    """
    INPUT: none
    """
    cur=mysql.get_db().cursor()
    cur.execute('''
        update users set splash_index=%s where uid=%s
    ''',[current_app.config['INITIAL_SPLASH_INDEX'],g.user.uid])

    flash('已重置欢迎页面进度','success')
    raise SisterProceed()