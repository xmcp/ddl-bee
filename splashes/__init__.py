from .base import SplashHandler
from sister import SisterErrorMsg

class SplashAlphaTestAgreement(SplashHandler):
    def __init__(self):
        super().__init__(0,'Alpha测试注意事项','announce_checker')

    def handout(self,uid):
        return {
            'title': 'Alpha 测试用户须知',
            'instruction_html': '<p>本项目处于 Alpha 测试阶段，请注意以下事项。</p>',
            'content_html': (
                '<p>本项目正在开发中，目前<b>对用户数据的可用性、完整性、保密性不做任何保证</b>。</p>'
                '<p>如果继续使用，<b>您在本项目的数据有可能丢失或泄漏</b>。没有人对此负任何责任。</p>'
                '<p>因此，在测试期间<b>请勿提交任何隐私或重要信息</b>。</p>'
            ),
            'check': '我同意',
        }

    def handin(self,uid,args):
        if not args.get('agree',None):
            self.flash('请同意注意事项','error')
        else:
            self.complete(uid)
            self.flash('完成','success')

SplashAlphaTestAgreement()