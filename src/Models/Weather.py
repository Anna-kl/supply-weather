import requests
import json
import pandas as pd
import datetime
from .config import Config
URL = 'https://localhost:44321/api/weather-restrictions/'
PARAM = ['rh', 'temp', 'wind_spd', 'wind_gust_spd', 'vis', 'clouds', 'snow',
         'pres']

PARAM_DICT = {'rh_n': 'Высокая влажность', 'temp_n': 'Критическая теспература', 'wind_gust_spd_n': 'Порывы ветрка',
              'clouds_n': 'Высокая облачность',
              'snow_n': 'Большое количество снега', 'vis_n': 'Плохая видимость'}


def normalize(data, min_n, max_n):
    if min_n == max_n:
        return 0
    return (data - min_n) / (max_n - min_n)


def datetime_handler(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    raise TypeError("Unknown type")


def calculated(data, param):
    max1 = max(data[param])
    min1 = min(data[param])
    data[param + '_n'] = data[param].apply(normalize, args=(min1, max1))
    return data


_config = Config('/config.ini')
_config.load_config()
api_key = _config.api_key()


class Weather:
    rh = None  # Влажность
    clouds = None  # облачность
    wind_spd = None  # скорость ветра
    temp = None  # температура
    wind_cdir = None  # Направление ветра
    slp = None  # давление
    vis = None  # видимость
    pres = None  # давление

    def __init__(self):
        pass
        # self.pres=args['pres']/1.334
        # self.rh=args['rh']
        # self.vis=args['vis']
        # self.clouds=args['clouds']
        # self.temp=args['temp']
        # self.wind_spd=args['wind_spd']
        # print('finish')

    def normalization(self, start_date, get_data, token):
        headers = {'Authorization':
                       'Bearer {}'.format(token),
                   'Content-type': 'application/json'}
        start = start_date - datetime.timedelta(days=3)
        end = start_date + datetime.timedelta(days=3)
        send = {"StartDate": start.strftime('%Y-%m-%d'), "EndDate": end.strftime('%Y-%m-%d'), "LocationIds": [1],
                "param": "hist"}
        r = requests.post(URL + 'get/', data=json.dumps(send), headers=headers,
                          verify=False)
        data = json.loads(r.content.decode())
        data = pd.DataFrame(data['items']).append(get_data, ignore_index=True)
        data['dttm'] = pd.to_datetime(data['dttm'], format='%Y-%m-%d').dt.date

        for param in PARAM:
            calculated(data, param)

        return data

    def analize(self, data, date_start, token):
        data = data.loc[data['dttm'] >= date_start]
        # Проверка грузоподемности
        winter = datetime.datetime.strptime('{0}-12-01'.format(date_start.year - 1), '%Y-%m-%d').date()
        summer = datetime.datetime.strptime('{0}-05-31'.format(date_start.year), '%Y-%m-%d').date()
        shape = data.shape
        analitics = []
        for i in range(0, shape[0]):
            s = data.iloc[[i]].to_dict('records')
            analitics.extend(s)
        for s in analitics:
            if date_start > winter and date_start < summer:
                if s['temp'] > 7:
                    s['restriction'] += 'Ограничения по погоде'

                if s['temp'] < -38 or s['wind_spd'] > 12:
                    if len(s['restriction']) > 0:
                        s['restriction'] += ','
                    s['restriction'] += 'Ограничения по погоде'

            else:
                for i in range(0, shape[0]):
                    s = data.iloc[[i]].to_dict('records')
                    if s['wind_spd'] > 12 or s[0]['wind_spd_gsp_n'] > 0.8:
                        s['restriction'] = 'Усиление ветра'

            for param in PARAM_DICT.keys():

                if s[param] > 0.9:
                    if len(s['warning']) > 0:
                        s['warning'] += ','
                    s['warning'] = PARAM_DICT[param]
        self.write_data(token, analitics)

    # def get_data(self):
    def get_data_now(self, lat, lng):
        # send ='{"StartDate": "2021-05-04","EndDate": "2021-05-05","LocationIds": [1], "param":"hist"}'
        # r = requests.post(url+'get/', data=send, headers=headers,
        #                 verify=False)
        r = requests.get(
            'https://api.weatherbit.io/v2.0/current?lat={0}&lon={1}&key={2}'.format(lat, lng, api_key['api_key']))
        data = json.loads(r.content.decode())
        self.send = {'rh': data['data'][0]['rh'], 'temp': data['data'][0]['temp'], "LocationIds": 1,
                     'pres': data['data'][0]['pres'] / 1.334, "wind_spd": data['data'][0]['wind_spd'],
                     "clouds": data['data'][0]['clouds'],
                     "lng": lng, "lat": lat, "snow": data['data'][0]['snow'],
                     'vis': data['data'][0]['vis'], 'dttm': data['data'][0]['ob_time']}
        return self.send

    def get_data_forecast_day(self, lat, lng, days):
        # send ='{"StartDate": "2021-05-04","EndDate": "2021-05-05","LocationIds": [1], "param":"hist"}'
        # r = requests.post(url+'get/', data=send, headers=headers,
        #                 verify=False)
        r = requests.get('https://api.weatherbit.io/v2.0/'
                         'forecast/daily?lat={0}&lon={1}&key={2}'.
                         format(lat, lng,
                                                                                                        api_key[
                                                                                                            'api_key']))
        data = json.loads(r.content.decode())
        get_data = []
        for i in range(0, days):
            send = {'rh': data['data'][i]['rh'], 'temp': data['data'][i]['temp'], "locationId": 1,
                    'pres': data['data'][i]['pres'] / 1.334, "wind_spd": data['data'][i]['wind_spd'],
                    "clouds": data['data'][i]['clouds'], 'wind_gust_spd': data['data'][i]['wind_gust_spd'],
                    "lng": lng, "lat": lat, "snow": data['data'][i]['snow'],
                    'vis': data['data'][i]['vis'], 'dttm': data['data'][i]['datetime'], 'restriction': '',
                    'warning': ''}
            get_data.append(send)
        return get_data

    def write_data(self, token, data):

        headers = {'Authorization':
                       'Bearer {}'.format(token),
                   'Content-type': 'application/json'}
        for d in data:
            d['dttm'] = str(d['dttm'])
            d['snow'] = int(d['snow'])
            d['id'] = 0
            send = json.dumps(d)
            r = requests.post('https://localhost:44321/api/weather-restrictions/addparam', data=send, headers=headers,
                              verify=False)
            print(r.content)
        return r.status_code
        # str1 = 'SELECT id, "temp", wind_spd, pres, snow, clouds, rh, vis, lat, lng, locationids, dttm, wind_gust_spd' \
        #        ' FROM public.weather_params where locationids={0} and ('.format(location)
        # for i in range(2016, 2022):
        #     data_start = data_start.replace(year=i)
        #     data_end = data_end.replace(year=i)
        #     str1 += '(dttm>=\'{0}\' and dttm>=\'{1}\') or '.format(data_start, data_end)
        # str1 = str1[0:len(str1) - 4]
        # str1 += ' )'
        # data = pd.read_sql_query(sql=str1, con=self.con, index_col=None)
        # for param in PARAM:
        #     calculated(data, param)
        # res = data.loc[data['dttm'] == data_start]
        # return res
    #   headers = {'Authorization':
    #                  'Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IjlEM0YyNDA0MEQ2QUZCODdCQjhDMkNBQjMwOEU4OUQwNEUwQzhCOTYiLCJ0eXAiOiJhdCtqd3QiLCJ4NXQiOiJuVDhrQkExcS00ZTdqQ3lyTUk2SjBFNE1pNVkifQ.eyJuYmYiOjE2MjAyOTAzMzcsImV4cCI6MTYyMDI5MjEzNywiaXNzIjoiaHR0cHM6Ly90ZXN0LmFjdHVhbC5zdXBwbHkiLCJhdWQiOiJhcGkiLCJjbGllbnRfaWQiOiJqcyIsInN1YiI6IjUyIiwiYXV0aF90aW1lIjoxNjIwMjg1MDk1LCJpZHAiOiJHb29nbGUiLCJzY29wZSI6WyJvcGVuaWQiLCJwcm9maWxlIiwiYXBpIl0sImFtciI6WyJleHRlcm5hbCJdfQ.jClYimLGMy_eVxNcTr6alb4OYAmU_XjZD5BimfdcrdVAwPVQoJe0nP4RNkRYpkEdeMEfpePcmKDzkbYUCk51yQs_eHGrB1ZU-xd2uAO66djmQ2VezVaJAZXPaBlTc64zUn6Fp2Wlra7UIE3bp3dVfoJhzGfkGCFXlLWXz2YchhhyCU49b2d-0tYjIkRQzKoUq7JmKM2lMpVPnkbtLdAmhOWIonESq0cTIjVA9PrH79FqiKrZOF6uN0gox2Yl0ByDE1wLkbckR21WtM8JUlB0K9gP8SMCpgwhtE4WHfPYGrolWGK2xmYP7etc0bPRLFae1OiEnuOOnJJ17skwzUXy3Q',
    #              'Content-type':'application/json'}
    #   # headers={}
    #   # headers.
    #   send ='{"StartDate": "2021-05-04","EndDate": "2021-05-05","LocationIds": [1]}'
    #
    # #  send='{"id":"eb527de3407449f9a014cb05f671dbf3","created":1620221835,"request_type":"si:s","nonce":"a6781988c43e4371bbd563f889f5d08d","redirect_uri":"http://localhost:8080/silent-renew.html","authority":"https://test.actualsupply.net","client_id":"js","response_mode":null,"scope":"openid profile api","extraTokenParams":{}}'
    #   r = requests.post(url+'get/', data=send, headers=headers,
    #                     verify=False)
    #
    #   weather_param=json.loads(r.content.decode())
    #   return weather_param
