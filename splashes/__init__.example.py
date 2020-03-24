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

SplashEULA()

class SplashTutorial(SplashHandler):
    def __init__(self):
        super().__init__(1,'新手教程','tutorial_1')

    def handout(self,_uid):
        return {}

    def handin(self,uid,_args):
        self.complete(uid)

SplashTutorial()

class SplashSurveySingle(SplashHandler):
    def __init__(self):
        super().__init__(2,'用户调查（单选）','select_single')

    def handout(self,_uid):
        return {
            'title': '用户调查（单选）',
            'instruction_html':'<p>请配合完成调查</p>',
            'content_html': '<p>请选择第二项</p>',
            'selection': [
                ['v1','text 1'],
                ['v2','text 2'],
                ['v3','text 3'],
            ],
            'default_selection': None,#'v1'
        }

    def handin(self,uid,args):
        sel=args.get('selection',None)
        self.flash('你选择了 '+sel,'info')
        if sel=='v2':
            self.complete(uid)

SplashSurveySingle()

class SplashSurveyMultiple(SplashHandler):
    def __init__(self):
        super().__init__(3,'用户调查（多选）','select_multiple')

    def handout(self,_uid):
        return {
            'title': '用户调查（多选）',
            'instruction_html':'<p>请配合完成调查</p>',
            'content_html': '<p>请选择第二项</p>',
            'selection': [
                ['v1','text 1'],
                ['v2','text 2'],
                ['v3','text 3'],
            ],
            'default_selection': ['v1','v2','v3'],
        }

    def handin(self,uid,args):
        sel=args.get('selection',None)
        self.flash('you selected '+str(sel),'info')
        if sel==['v2']:
            self.complete(uid)

SplashSurveyMultiple()