from flask import *
from mysql import mysql

def _set_splash_index(uid,next_index):
    cur=mysql.get_db().cursor()
    cur.execute('''
        update users set splash_index=%s where uid=%s
    ''',[next_index,uid])

class SplashHandler:
    _registered_handlers={}

    @classmethod
    def get_handler_by_index(cls,splash_index):
        """ Return handler for specified index, or None
        :rtype: SplashHandler
        """
        return cls._registered_handlers.get(splash_index,None)

    def __init__(self,splash_index,splash_name,splash_type):
        if SplashHandler._registered_handlers.get(splash_index,self) is not self:
            raise ValueError('splash index already registered to another handler')
        SplashHandler._registered_handlers[splash_index]=self
        self.splash_index=splash_index
        self.splash_name=splash_name
        self.splash_type=splash_type

    def complete(self,uid):
        _set_splash_index(uid,self.splash_index+1)

    @staticmethod
    def flash(msg,cat='message'):
        flash(msg,cat)

    def handout(self,uid):
        raise NotImplementedError('should override SplashHandler.handout in #%d'%self.splash_index)

    def handin(self,uid,args):
        raise NotImplementedError('should override SplashHandler.handin in #%d'%self.splash_index)