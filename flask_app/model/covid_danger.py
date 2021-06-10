import json

import pandas as pd
import numpy as np

import joblib
from sklearn.neighbors import KernelDensity
from sklearn.preprocessing import Normalizer
from sklearn.pipeline import Pipeline

import time

import os
import requests
from bs4 import BeautifulSoup


# -----------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------기타 함수들-------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------

# 각 시별 자치구 개수 파악
# ex) 성남의 자치구 수를 파악할 때: district_num(info_dict, "성남")

def district_num(info_dict, super_class):
   n = 0
   try:
      for key in info_dict.keys():
         if (key == super_class):
            return len(info_dict[key].keys())

      for key in info_dict.keys():
         n = max(n, district_num(info_dict[key], super_class))

      return n

   except AttributeError:
      return n


def get_total_districts_num(info_dict, prov):
  n = 0
  try:
    for city in info_dict[prov].keys():
      n += get_total_districts_num(info_dict[prov], city)
    return n
  except AttributeError:
    return 1


# 각 자치구의 [위도, 경도] 반환

def get_geo_vector(info_dict, district_name):
  vector = 0
  try:
    for key in info_dict.keys():
      if (key == district_name):
        return info_dict[key]

    for key in info_dict.keys():
      ret = get_geo_vector(info_dict[key], district_name)
      if (ret != 0):
        vector = ret
    return vector

  except:
    return vector


# 위경도상 반경 300m 적분.
def numerical_2Dintegral(function, x, y, delta_x=0.07, delta_y=0.08, dx=0.01, dy=0.01):
  m_xx = np.linspace(x, x + dx, int(delta_x/dx))
  m_yy = np.linspace(y, y + dy, int(delta_y/dy))

  m_X, m_Y = np.meshgrid(m_xx, m_yy)
  domain = np.array([m_X.ravel(), m_Y.ravel()]).T

  f_values = np.sum(np.exp(function.score_samples(domain)))  #function needs to be a scikit learn estimator
  return f_values * dx * dy


# 코로나 위험도 계산
def calc_critical_score(func, x, y, n=10, time=4):
  return numerical_2Dintegral(func, x, y) * 100 / n * np.log(time + 1) / 1.6 * 100


# --------------------------------------------------------------------------------------------------------------
#
#           seoul_cases: 서울 자치구별 확진자 데이터가 들어있는 딕셔너리
#           gyunggi_cases: 경기도 각 시별 확진자 데이터가 들어있는 딕셔너리
#           other_cases: 기타 지역 시,도별 확진자 데이터가 들어있는 딕셔너리
#           geo_info_dict: 각 자치구의 위도, 경도 데이터가 들어있는 딕셔너리
#
#
#
# --------------------------------------------------------------------------------------------------------------



# 모델 생성
def create_model(save_path, path):
   # 지리 데이터 json 열기, path가 경로

   # path = os.path.join(os.getcwd(), "/flask_app/data/geo_dict.json")
   with open(path, 'r') as f:
       geo_info_dict = json.load(f)

   geo_info_dict = json.loads(json.dumps(geo_info_dict, ensure_ascii=False))


   date = time.strftime('%Y-%m-%d', time.localtime(time.time()))

   # ----------------------------------------------------------------------------------------------------------------
   # --------------------------------------------------코로나 현황 크롤링--------------------------------------------
   # ----------------------------------------------------------------------------------------------------------------
   # 서울
   response = requests.get('https://www.seoul.go.kr/coronaV/coronaStatus.do')
   soup = BeautifulSoup(response.content, 'html.parser')

   ths = soup.select("table.tstyle-status.pc.pc-table > tbody > tr > th")
   tds = soup.select("table.tstyle-status.pc.pc-table > tbody > tr > td.today")

   seoul_cases = {}

   for th, td in zip(ths, tds):
      seoul_cases[th.text.replace(" ", "")] = int(td.text)

   del seoul_cases["기타"]


   # 경기 코로나 확진자 현황 크롤링
   response = requests.get('https://www.gg.go.kr/contents/contents.do?ciIdx=1150&menuId=2909')
   soup = BeautifulSoup(response.content, 'html.parser')

   districts = soup.select("#result > div.mt-4.py-4.w-100 > div > div > dl > dt")
   cases = soup.select("#result > div.mt-4.py-4.w-100 > div > div > dl > dd > small.count")

   del districts[0]
   gyunggi_cases = {}

   for region, case in zip(districts, cases):
      gyunggi_cases[region.text.replace(" ", "")] = int(case.text[6:])


   # 기타 지역 코로나 확진자 현황 크롤링
   response = requests.get('http://ncov.mohw.go.kr/bdBoardList_Real.do?brdId=1&brdGubun=13&ncvContSeq=&contSeq=&board_id=&gubun=')
   soup = BeautifulSoup(response.content, 'html.parser')

   ths = soup.select("table.num.midsize > tbody > tr > th")
   tds = soup.select("table.num.midsize > tbody > tr > td:nth-of-type(1)")

   other_cases = {}
   for th, td in zip(ths, tds):
      other_cases[th.text.replace(" ", "")] = int(td.text)

   del other_cases["합계"], other_cases["검역"], other_cases["서울"], other_cases["경기"]


   # ----------------------------------------------------------------------------------------------------------------
   # ------------------------------------------   학습데이터 생성    ------------------------------------------------
   # ----------------------------------------------------------------------------------------------------------------

   X_train = np.zeros((1, 2), dtype=np.float64)

   # 서울 학습데이터
   for region in seoul_cases.keys():
      xy = get_geo_vector(geo_info_dict, region)

   for i in range(seoul_cases[region]):
      coordi = np.array(xy)
      X_train = np.vstack((X_train, coordi))


   # 경기 학습데이터
   for city in (gyunggi_cases.keys()):
      # 시 이하에 자치구가 있을 경우
      if isinstance(geo_info_dict["경기"][city], dict):

         districts_num = len(geo_info_dict["경기"][city].keys())
         distributed_num = int (gyunggi_cases[city] / districts_num)

         for district in geo_info_dict["경기"][city].keys():
            for i in range(distributed_num):
               coordi = np.array(geo_info_dict["경기"][city][district])
               X_train = np.vstack((X_train, coordi))

         # 확진자 수가 자치구 수로 나누어 떨어지지 않는 경우 남는 수를 첫번째 도시에 배정함.
         for i in range(gyunggi_cases[city] - districts_num * distributed_num):
            coordi = np.array(geo_info_dict["경기"][city][list(geo_info_dict["경기"][city].keys())[0]])
            X_train = np.vstack((X_train, coordi))

      # 아닐경우
      else:
         for i in range(gyunggi_cases[city]):
            coordi = geo_info_dict["경기"][city]
            X_train = np.vstack((X_train, coordi))


   province_names = ["강원", "충북", "충남", "전북", "전남", "경남", "경북", "제주"]
   city_names = ["인천", "세종", "대전", "대구", "광주", "울산", "부산"]


   # 타지역 도 학습데이터
   for prov in province_names:
      districts_num = get_total_districts_num(geo_info_dict, prov)
      distributed_num = int (other_cases[prov] / districts_num)

      for city in geo_info_dict[prov].keys():

         # 시 이하에 자치구가 있을 경우
         if isinstance(geo_info_dict[prov][city], dict):
            # if (gyunggi_cases[city] % len(geo_info_dict["경기"][city].keys()) != 0) and (gyunggi_cases[city] != 0):
            # print("누락발생!")
            distributed_num = int (other_cases[prov] / districts_num)

            for district in geo_info_dict[prov][city].keys():
               for i in range(distributed_num):
                  coordi = np.array(geo_info_dict[prov][city][district])
                  X_train = np.vstack((X_train, coordi))

            # 확진자 수가 자치구 수로 나누어 떨어지지 않는 경우 남는 수를 첫번째 도시에 배정함.
            for i in range(other_cases[prov] - districts_num * distributed_num):
               coordi = np.array(geo_info_dict[prov][city][list(geo_info_dict[prov][city].keys())[0]])
               X_train = np.vstack((X_train, coordi))

         # 아닐경우
         else:
            for i in range(distributed_num):
               coordi = np.array(geo_info_dict[prov][city])
               X_train = np.vstack((X_train, coordi))


   # 타지역 시 학습데이터
   for city in city_names:
      districts_num = get_total_districts_num(geo_info_dict, city)
      distributed_num = int (other_cases[city] / districts_num)

      for district in geo_info_dict[city].keys():
         for i in range(distributed_num):
            coordi = np.array(geo_info_dict[city][district])
            X_train = np.vstack((X_train, coordi))

      # 확진자 수가 자치구 수로 나누어 떨어지지 않는 경우 남는 수를 첫번째 도시에 배정함.
      for i in range(other_cases[city] - districts_num * distributed_num):
         coordi = np.array(geo_info_dict[city][list(geo_info_dict[city].keys())[0]])
         X_train = np.vstack((X_train, coordi))



   # 극데이터 추가// 전체 데이터에 미칠영향 평가 필요
   for end in geo_info_dict["기타"].keys():
      coordi = geo_info_dict["기타"][end]
      X_train =np.vstack((X_train, coordi))


   idx = [1, 0]

   X_train = np.delete(X_train, 0, axis=0)
   X_train = X_train[:, idx]
   # --------------------------------------------------------밀도예측----------------------------------------------------------------------

   pipeline = Pipeline([
                     ('kde', KernelDensity(bandwidth=0.03, kernel='gaussian'))
   ])

   pipeline.fit(X_train)
   model = joblib.dump(pipeline, save_path)


def load_model(path):
   return joblib.load(path)




if __name__ == "__main__":
   create_model(r"/home/COVID19danger/mysite/flask_app/model/model.pkl", r"/home/COVID19danger/mysite/flask_app/data/geo_dict.json")

