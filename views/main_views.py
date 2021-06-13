from flask import Blueprint, render_template, request
from flask_app.model import covid_danger as cd
import os, json

bp = Blueprint('main', __name__, url_prefix='/')
# question = ["어디로 가시나요?", "얼마나 머무르시나요?", "당신의 코로나19 위험도 점수는"]
# path = r"/home/COVID19danger/mysite/flask_app/model/model.pkl"
path = os.path.join(os.getcwd(), r"flask_app/model/model.pkl")
tmo_data_path =  os.path.join(os.getcwd(), r"flask_app/data/tmo_data.csv")


model = cd.load_model(path)

@bp.route('/')
def syte_inspection():
    return render_template('index.html')



@bp.route('/', methods=['POST'])
def test_print():
    location = request.form['coordi'].split(',')
    result_dict = {}
    
    time = float(request.form['time'])
    x, y = float(location[0]), float(location[1])
    
    tmo_name, tmo_dist = cd.calc_distance(tmo_data_path, [y, x])
    # print(tmo_name, tmo_dist)
    
    score = cd.calc_critical_score(model, x, y, time=time)
    
    result_dict["tmo_name"] = tmo_name
    result_dict["tmo_dist"] = format(tmo_dist, ".1f")
    result_dict["score"] = format(score, ".1f")
    
    return json.dumps(result_dict, ensure_ascii=False)


@bp.route('/ing')
def test():
    return 'ING is so cute!'

