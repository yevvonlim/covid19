from covid_danger import create_model
import requests

username = "COVID19danger"
api_token = "6cc1c082865cc7e0ec949deae9629bb5c39ab658"
domain_name = "covid19danger.pythonanywhere.com"

create_model(r"/home/COVID19danger/mysite/flask_app/model/model.pkl", r"/home/COVID19danger/mysite/flask_app/data/geo_dict.json")

response = requests.post(
    'https://www.pythonanywhere.com/api/v0/user/{username}/webapps/{domain_name}/reload/'.format(
        username=username, domain_name=domain_name
    ),
    headers={'Authorization': 'Token {token}'.format(token=api_token)}
)
if response.status_code == 200:
    print('reloaded OK')
else:
    print('Got unexpected status code {}: {!r}'.format(response.status_code, response.content))