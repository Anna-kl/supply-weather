import requests
import json
import pandas as pd
import datetime
import os

PARAM = ['Rh', 'Temp', 'WindSpd', 'WindGustSpd', 'Vis', 'Clouds', 'Snow',
         'Pres']

PARAM_DICT = {'Rh_n': 'Высокая влажность', 'WindGustSpd_n': 'Порывы ветра',
              'Clouds_n': 'Высокая облачность',
              'Snow_n': 'Большое количество снега', 'Vis_n': 'Плохая видимость'}


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


api_key=os.environ['api_key']
# api_key = '48c910f8c4054b3cac5a84da4013c0d9'


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

    def normalization(self, start_date, get_data, token, locations):
        headers = {'Authorization':
                       'Bearer {}'.format(token),
                   'Content-type': 'application/json'}
        start = start_date
        end = start
        type = {'Id': 1, 'Name': 'History'}
        type = json.dumps(type)
        send = {"StartDate": start.strftime('%Y-%m-%d'), "EndDate": end.strftime('%Y-%m-%d'),
                "LocationIds": [locations], "param": type}
        r = requests.post(os.environ['URL'] + 'get/', data=json.dumps(send),
                          headers=headers,
                          verify=False)
        data = json.loads(r.content.decode())
        data = pd.DataFrame(data['items']).append(get_data, ignore_index=True)
        data['Dttm'] = pd.to_datetime(data['Dttm'], format='%Y-%m-%d').dt.date
        data['Warning'] = ''
        for param in PARAM:
            calculated(data, param)

        return data

    def analize(self, data, date_start, token):
        data = data.loc[data['Dttm'] >= date_start]

        winter = datetime.datetime.strptime('{0}-12-01'.format(date_start.year - 1), '%Y-%m-%d').date()
        summer = datetime.datetime.strptime('{0}-05-31'.format(date_start.year), '%Y-%m-%d').date()
        shape = data.shape
        analitics = []
        for i in range(0, shape[0]):
            s = data.iloc[[i]].to_dict('records')[0]
            if date_start > winter and date_start < summer:

                if s['Temp'] < -38 or s['WindSpd'] > 12 or s['WindGustSpd'] > 12:
                    if len(s['Warning']) > 0:
                        s['Warning'] += ','
                    s['Warning'] += 'Ограничения по погоде'

            else:
                if s['WindSpd'] > 12 or s['WindGustSpd'] > 0.8:
                        if len(s['Warning']) > 0:
                            s['Warning'] += ','
                        s['Warning'] += 'Усиление ветра'
            if s['Temp'] > 30:
                        if len(s['Warning']) > 0:
                            s['Warning'] += ','
                        s['Warning'] += 'Высокая температура'
            elif s['Temp'] < -30:
                        if len(s['Warning']) > 0:
                            s['Warning'] += ','
                        s['Warning'] += 'Низкая температура'

            for param in PARAM_DICT.keys():

                if s[param] > 0.99:
                    if len(s['Warning']) > 0:
                        s['Warning'] += ','
                    s['Warning'] += PARAM_DICT[param]
            analitics.append(s)
        self.write_data(token, analitics)

    def get_location(self, token):
        request = {
            'Statuses': None,
            'ParentIds': None,
            'Ids': None,
            'Types': None
        }
        headers = {'Authorization':
                       'Bearer {}'.format(token),
                   'Content-type': 'application/json'}
        r = requests.post(os.environ['URL_Locations'], data=json.dumps(request), headers=headers,
                          verify=False)
        locations = json.loads(r.content)
       # locations = list(filter(lambda x: len(x['childrenIds']) == 0, locations))
        return locations

    # def get_data(self):

    def get_data_forecast_day(self, lat, lng, days, locations):
        # send ='{"StartDate": "2021-05-04","EndDate": "2021-05-05","LocationIds": [1], "param":"hist"}'
        # r = requests.post(url+'get/', data=send, headers=headers,
        #                 verify=False)
        r = requests.get(
            'https://api.weatherbit.io/v2.0/forecast/daily?lat={0}&lon={1}&key={2}'.format(lat, lng, api_key))
        data = json.loads(r.content.decode())
        get_data = []
        for i in range(0, days):
            send = {'Rh': data['data'][i]['rh'], 'Temp': data['data'][i]['temp'], "LocationId": locations,
                    'Pres': data['data'][i]['pres'] / 1.334, "WindSpd": data['data'][i]['wind_spd'],
                    "Clouds": data['data'][i]['clouds'], 'WindGustSpd': data['data'][i]['wind_gust_spd'],
                    "lng": lng, "lat": lat, "Snow": data['data'][i]['snow'],
                    'Vis': data['data'][i]['vis'], 'Dttm': data['data'][i]['datetime'], 'Restriction': '',
                    'Warning': ''}
            get_data.append(send)
        return get_data

    def write_data(self, token, data):

        headers = {'Authorization':
                       'Bearer {}'.format(token),
                   'Content-type': 'application/json'}
        for d in data:
            d['Dttm'] = str(d['Dttm'])
            d['Snow'] = int(d['Snow'])
            d['id'] = 0
            send = json.dumps(d)
            r = requests.post(os.environ['URL'] + 'addupdateparam', data=send,
                              headers=headers,
                              verify=False)

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
