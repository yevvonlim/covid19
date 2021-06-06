from flask import Blueprint, render_template


bp = Blueprint('main', __name__, url_prefix='/')
# question = ["어디로 가시나요?", "얼마나 머무르시나요?", "당신의 코로나19 위험도 점수는"]


@bp.route('/')
def syte_inspection():
    return render_template('index.html')


"""
@bp.route('/', methods=['POST'])
def test_print():
    score = request.form['text']
    return render_template('question/question_list.html',
                        question_list=question, score=score)
"""


@bp.route('/ing')
def test():
    return 'ING is so cute!'
