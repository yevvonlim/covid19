from flask import Blueprint, render_template, request
from flask_app.model import covid_danger as cd

bp = Blueprint('main', __name__, url_prefix='/')
# question = ["어디로 가시나요?", "얼마나 머무르시나요?", "당신의 코로나19 위험도 점수는"]
path = r"/workspace/covid19/flask_app/model/model.pkl"
model = cd.load_model(path)

@bp.route('/')
def syte_inspection():
    return render_template('index.html')



@bp.route('/', methods=['POST'])
def test_print():
    location = request.form['location'].split(',')
    time = float(request.form['time'])
    x, y = float(location[1]), float(location[0])
    
    score = cd.calc_critical_score(model, x, y, time=time)
    
    return render_template('index.html',
                      num=str(score))



@bp.route('/ing')
def test():
    return 'ING is so cute!'
