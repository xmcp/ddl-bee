from .base import SplashHandler

class SplashEULA(SplashHandler):
    def __init__(self):
        super().__init__(0,'用户须知','announce_checker')

    def handout(self,_uid):
        return {
            'title': '用户须知',
            'instruction_html': '<p>请同意用户须知。</p>',
            'content_html': (
                '<p><b>Obey or die.</b></p>'
            ),
            'check': '我同意',
        }

    def handin(self,uid,args):
        if not args.get('agree',None):
            self.flash('你必须同意','error')
        else:
            self.complete(uid)
            self.flash('完成','success')

SplashEULA()

class SplashTutorial(SplashHandler):
    def __init__(self):
        super().__init__(1,'新手教程','announce')

    def handout(self,_uid):
        return {
            'title': '新手教程',
            'content_html': (
                '<p>自己琢磨去。</p>'
            ),
        }

    def handin(self,uid,_args):
        self.complete(uid)
        self.flash('完成','success')

SplashTutorial()