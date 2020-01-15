from flask import *

from sister import use_sister

bp=Blueprint('refresh',__name__)

@bp.route('/refresh')
@use_sister()
def refresh():
    pass # sister will deal with it