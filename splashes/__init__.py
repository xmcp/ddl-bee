from .base import SplashHandler
from sister import SisterErrorMsg

class SplashAlphaTestAgreement(SplashHandler):
    def __init__(self):
        super().__init__(0,'Alpha测试注意事项')

    def handout(self,uid):
        return {
            'msg': '本项目处于测试阶段，请注意以下事项。'
        }

    def handin(self,uid,args):
        if not args.get('agree',None):
            self.flash('请同意注意事项','error')
        else:
            self.complete(uid)
            self.flash('完成','success')

SplashAlphaTestAgreement()