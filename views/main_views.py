from flask import Blueprint

bp = Blueprint('main', __name__, url_prefix='/')


@bp.route('/')
def syte_inspection():
    return '곧 지역별 코로나 위험도 예측 서비스가 시작될 예정입니다.'
    
    
@bp.route('/ing')
def test():
    return 'ING is so cute!'
