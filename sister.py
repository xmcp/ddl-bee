from flask import *
from mysql import mysql
from functools import wraps

import model
import splashes

class SisterErrorMsg(Exception):
    def __init__(self,msg):
        self.msg=msg

VERSION='VERSION'
NOTIFS=[['本项目正在测试','message']]

def _backend_value():
    return {
        'version': VERSION,
        'flash_msgs': get_flashed_messages(with_categories=True),
        'sticky_msgs': NOTIFS,
    }

def use_sister(enforce_auth=True, enforce_splash=True):
    """ Decorator for view functions.
    SHOULE BE USED FOR EVERY VIEW FUNCTION!

    - Provides g.user and authentication with `user_token` arg
    - Deals with exceptions
    - Provides splash control
    - Commits database if no error
    - Adds `backend`, `user`, `error` key in response
    - Provides default build_sister_response if view function returns None
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args,**kwargs):
            g.user=None
            db=mysql.get_db()

            # check auth and init g.user

            g.token=request.args.get('user_token',None)
            if g.token:
                cur=db.cursor()
                cur.execute(
                    'select uid,name,ring,splash_index,settings from users where user_token=%s',
                    [g.token]
                )
                res=cur.fetchone()
                if res:
                    uid,name,ring,splash_index,settings=res
                    g.user=model.User(uid,name,ring,splash_index,settings)

            if g.user is None and enforce_auth:
                return jsonify({
                    'error': 'AUTH_REQUIRED',
                    'error_msg': '需要登录',
                    'backend': _backend_value(),
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
                            'handout': handler.handout(g.user.uid),
                        },
                    })

            # do original view function

            try:
                res=f(*args,**kwargs)

                # check for default sister response

                if res is None:
                    res=g.user.build_sister_response()

            # error handling

            except SisterErrorMsg as e:
                return jsonify({
                    'error': 'SISTER_ERROR',
                    'error_msg': e.msg,
                    'backend': _backend_value(),
                })
            except Exception as e:
                current_app.logger.exception('exception in wrapped handler')
                return jsonify({
                    'error': 'BACKEND_EXCEPTION',
                    'error_msg': '后端错误 %s %s'%(type(e),e),
                    'backend': _backend_value(),
                })

            # post processing

            else:
                db.commit()
                return jsonify({
                    'error': None,
                    'backend': _backend_value(),
                    'user': None if g.user is None else g.user.user_info(),
                    **res,
                })

        return decorated

    return decorator