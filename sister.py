from flask import *
from flask_cors import cross_origin

import os
from mysql import mysql
from functools import wraps

class SisterErrorMsg(Exception):
    def __init__(self,msg):
        self.msg=msg

class SisterProceed(Exception):
    pass

import user_control
import model
import splashes

COMPATIBLE_SISTER_VER=['4','4a']
CACHE_DATA_VER='4'

def get_git_revision():
    try:
        with open('.git/HEAD') as head:
            ref = head.readline().split(' ')[-1].strip()

        with open(os.path.join('.git',ref)) as git_hash:
            return git_hash.readline().strip()
    except Exception as e:
        print('! get version from git failed:',type(e),e)
        return '???'

VERSION=os.environ.get('BEE_ENV_NAME','')+get_git_revision()[:6]

def _backend_value():
    return {
        'version': VERSION,
        'flash_msgs': get_flashed_messages(with_categories=True),
        'sticky_msgs': user_control.sticky_msg(g.user,request.endpoint),
        'cache_data_ver': CACHE_DATA_VER,
    }

def get_user_from_token(token):
    cur=mysql.get_db().cursor()
    cur.execute(
        'select uid,name,ring,splash_index,settings from users where user_token=%s',
        [token]
    )
    res=cur.fetchone()
    if res:
        uid,name,ring,splash_index,settings=res
        return model.User(uid,name,ring,splash_index,settings)
    else:
        return None

def use_sister(enforce_splash=False, require_ring=4, may_fallback=True):
    """ Decorator for view functions.
    SHOULE BE USED FOR EVERY VIEW FUNCTION!
    :param enforce_splash: set to False will disable SPLASH_REQUIRED error
    :param require_ring: max ring to use this view. set to None will disable authentication at all
    :param may_fallback: may return model data as default response

    - Checks api version
    - Provides g.user and authentication with `user_token` arg
    - Provides g.action_success
    - Deals with exceptions
    - Provides splash control
    - Commits database if no error
    - Adds `backend`, `user`, `error` key in response
    - Provides default build_sister_response if view function returns None
    """

    def decorator(f):
        @wraps(f)
        @cross_origin()
        def decorated(*args,**kwargs):

            # check api version

            client_api_ver=request.args.get('sister_ver',None)
            if client_api_ver not in COMPATIBLE_SISTER_VER:
                return jsonify({
                    'error': 'SISTER_VER_MISMATCH',
                    'error_msg': 'API 版本与后端 (Sister %s) 不兼容'%(', '.join(COMPATIBLE_SISTER_VER)),
                })

            g.user=None
            g.action_success=True

            # check auth and init g.user

            g.token=request.args.get('user_token',None)
            if g.token:
                g.user=get_user_from_token(g.token)

            if require_ring is not None:
                if g.user is None:
                    return jsonify({
                        'error': 'AUTH_REQUIRED',
                        'error_msg': '需要登录',
                        'backend': _backend_value(),
                    })
                elif g.user.ring>require_ring:
                    return jsonify({
                        'error':'SISTER_ERROR',
                        'error_msg':'你所在的用户组不支持此操作',
                        'backend':_backend_value(),
                    })

            # check splash

            if enforce_splash and g.user:
                handler=splashes.SplashHandler.get_handler_by_index(g.user.splash_index)
                if handler is not None:
                    return jsonify({
                        'error': 'SPLASH_REQUIRED',
                        'error_msg': '需要更新前端来完成 %s'%handler.splash_name,
                        'backend':_backend_value(),
                        'splash': {
                            'index': handler.splash_index,
                            'name': handler.splash_name,
                            'type': handler.splash_type,
                            'handout': handler.handout(g.user.uid),
                        },
                    })

            # do original view function

            try:
                res=f(*args,**kwargs)

                # check for default sister response

                if res is None:
                    if g.user and may_fallback:
                        res=g.user.build_sister_response()
                    else:
                        raise Exception('no available response')

            # error handling

            except SisterErrorMsg as e:
                return jsonify({
                    'error': 'SISTER_ERROR',
                    'error_msg': e.msg,
                    'backend': _backend_value(),
                })
            except SisterProceed:
                mysql.get_db().commit()
                return jsonify({
                    'error': 'PROCEED',
                    'error_msg': '操作完成，请刷新页面',
                    'backend': _backend_value(),
                })
            except Exception as e:
                current_app.logger.exception('exception in wrapped handler')
                return jsonify({
                    'error': 'BACKEND_EXCEPTION',
                    'error_msg': '%s %s'%(type(e),e),
                    'backend': _backend_value(),
                })

            # post processing

            else:
                mysql.get_db().commit()
                return jsonify({
                    'error': None,
                    'backend': _backend_value(),
                    'user': None if g.user is None else g.user.user_info(),
                    'action_success': g.action_success,
                    **res,
                })

        return decorated

    return decorator