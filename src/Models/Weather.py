import requests
import json
import pandas as pd
import datetime
import os

PARAM = ['temp', 'windSpd', 'windGustSpd', 'vis', 'clouds', 'snow']

PARAM_DICT = {'windGustSpd_n': 'Порывы ветра',
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


#api_key=os.environ['api_key']
api_key = '48c910f8c4054b3cac5a84da4013c0d9'


class Weather:
    clouds = None  # облачность
    wind_spd = None  # скорость ветра
    temp = None  # температура
    wind_cdir = None  # Направление ветра
    slp = None  # давление
    vis = None  # видимость

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
                "GraphFilter":{'LocationsIds': [locations]}, "param": type}
        r = requests.post('https://monitoring.gpn.supply/api/contexts/1/weather-restrictions/' + 'get/', data=json.dumps(send),
                          headers=headers,
                          verify=False)
        # r = requests.post('https://localhost:44321/api/contexts/1/weather-restrictions/' + 'get/', data=json.dumps(send),
        #                                      headers=headers,
        #                                      verify=False)
        data = json.loads(r.content.decode())
        if data['items'].__len__() > 0:
            data = pd.DataFrame(data['items'][0]['payloads']).append(get_data, ignore_index=True)
        else:
            data = pd.DataFrame(get_data)
        #data = pd.DataFrame(data['items']).append(get_data, ignore_index=True)
        data['dttm'] = pd.to_datetime(data['dttm'], format='%Y-%m-%d').dt.date
        data['warning'] = ''
        data['locationId'] = locations
        for param in PARAM:
            calculated(data, param)

        return data
    

    def analize(self, data, date_start, token):
        data = data.loc[data['dttm'] >= date_start]

        winter = datetime.datetime.strptime('{0}-12-01'.format(date_start.year - 1), '%Y-%m-%d').date()
        summer = datetime.datetime.strptime('{0}-05-31'.format(date_start.year), '%Y-%m-%d').date()
        shape = data.shape
        analitics = []
        for i in range(0, shape[0]):
            s = data.iloc[[i]].to_dict('records')[0]
            if date_start > winter and date_start < summer:

                if s['temp'] < -38 or s['windSpd'] > 12 or s['windGustSpd'] > 12:
                    if len(s['restriction']) > 0:
                        s['restriction'] += ','
                    s['restriction'] += 'Ограничения по погоде'

            else:
                if s['windSpd'] > 10 or s['windGustSpd'] > 10:
                        if len(s['warning']) > 0:
                            s['warning'] += ','
                        s['warning'] += 'Усиление ветра'
            if s['temp'] > 30:
                        if len(s['warning']) > 0:
                            s['warning'] += ','
                        s['warning'] += 'Высокая температура'
            elif s['temp'] < -30:
                        if len(s['warning']) > 0:
                            s['warning'] += ','
                        s['warning'] += 'Низкая температура'

            for param in PARAM_DICT.keys():

                if s[param] > 0.99:
                    if len(s['warning']) > 0:
                        s['warning'] += ','
                    s['warning'] += PARAM_DICT[param]
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
        r = requests.post('https://monitoring.gpn.supply/api/contexts/1/locations/list', data=json.dumps(request), headers=headers,
                         verify=False)
        # r = requests.post('https://localhost:44321/api/contexts/1/locations/list', data=json.dumps(request), headers=headers,
        #                                      verify=False)
        locations = json.loads(r.content)
       # locations = list(filter(lambda x: len(x['childrenIds']) == 0, locations))
        return locations

    # def get_data(self):
    def get_data_forecast_day_route(self, coordinates, days, locations):
        # send ='{"StartDate": "2021-05-04","EndDate": "2021-05-05","LocationIds": [1], "param":"hist"}'
        # r = requests.post(url+'get/', data=send, headers=headers,
        #                 verify=False)
        all_data = []

        coordinates = coordinates.split(';')
        for i in range(0, days):
            get_data = {'icon': [], 'temp': [], "locationId": locations,
                        "windSpd": [],
                        "clouds": [], 'windGustSpd': [],
                        "lng": None, "lat": None,
                        "snow": [],
                        'vis': [], 'dttm': '',
                        'restriction': '',
                        'warning': ''}
            for coordinate in coordinates:

              try:
                coordinate = coordinate.split(',')
                get_data['lng'] = coordinate[1]
                get_data['lat'] = coordinate[0]
                r = requests.post(
                    'https://api.weatherbit.io/v2.0/forecast/daily?lat={0}&lon={1}&key={2}'.format(coordinate[0], coordinate[1], api_key))
                data = json.loads(r.content.decode())
                get_data["windSpd"].append(data['data'][i]['wind_spd'])
                get_data["temp"].append(data['data'][i]['temp'])
                get_data["clouds"].append(data['data'][i]['clouds'])
                get_data["windGustSpd"].append(data['data'][i]['wind_gust_spd'])
                get_data["snow"].append(data['data'][i]['snow'])
                get_data["vis"].append(data['data'][i]['vis'])
                get_data["dttm"] = data['data'][i]['datetime']
                get_data["icon"] = data['data'][i]['weather']['icon']
                get_data["clouds"].append(data['data'][i]['clouds'])
              except Exception as ex:
                  print(ex)
            all_data.append(get_data)
        return all_data

    def analitics_weather_route(self, all_data,token):
        all_day = []
        for day in all_data:
            get_data = {'icon': day['icon'],
                        'temp': None, "locationId": day['locationId'],
                        "windSpd": None,
                        "clouds": None, 'windGustSpd': None,
                        "lng": day['lng'], "lat": day['lng'],
                        "snow": None,
                        'vis': None, 'dttm': day['dttm'],
                        'restriction': '',
                        'warning': ''}

            for vis in day['vis']:
                if vis < 0.5:
                    get_data['vis'] = vis
                    get_data['warning'] += self.add_description(PARAM_DICT['vis_n'], get_data['warning'])
                    break
            if get_data['vis'] == None:
                get_data['vis'] = min(day['vis'])
            get_data['clouds'] = max(day['clouds'])
            for temp in day['temp']:
                if temp <= -38:
                    get_data['temp'] = temp
                    get_data['warning'] += self.add_description(PARAM_DICT['temp'], get_data['warning'])
                    break
            if get_data['temp'] == None:
                get_data['temp'] = min(day['temp'])
            for snow in day['snow']:
                if snow > 20:
                    get_data['snow'] = snow
                    get_data['warning'] += self.add_description(PARAM_DICT['snow_n'], get_data['warning'])
                    break
            if get_data['snow'] == None:
                get_data['snow'] = max(day['snow'])
            for wind in day['windSpd']:
                if wind > 15:
                    get_data['windSpd'] = wind
                    get_data['warning'] += self.add_description('Сильный ветер', get_data['warning'])
                    break
            if get_data['windSpd'] == None:
                get_data['windSpd'] = max(day['windSpd'])
            for wind in day['windGustSpd']:
                if wind > 20:
                    get_data['windGustSpd'] = wind
                    get_data['warning'] += self.add_description('Порывы ветра', get_data['warning'])
                    break
            if get_data['windGustSpd'] == None:
                get_data['windGustSpd'] = max(day['windGustSpd'])
            all_day.append(get_data)
        self.write_data(token, all_day)

    def add_description(self, text, original):
        if original != '':
            original += ','
        original += text

        return original

    def get_data_forecast_day(self, lat, lng, days, locations):
        # send ='{"StartDate": "2021-05-04","EndDate": "2021-05-05","LocationIds": [1], "param":"hist"}'
        # r = requests.post(url+'get/', data=send, headers=headers,
        #                 verify=False)
        r = requests.post(
            'https://api.weatherbit.io/v2.0/forecast/daily?lat={0}&lon={1}&key={2}'.format(lat, lng, api_key))
        data = json.loads(r.content.decode())
        get_data = []
        for i in range(0, days):
            send = {'icon': data['data'][i]['weather']['icon'], 'temp': data['data'][i]['temp'], "locationId": locations,
                     "windSpd": data['data'][i]['wind_spd'],
                    "clouds": data['data'][i]['clouds'], 'windGustSpd': data['data'][i]['wind_gust_spd'],
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
            d['clouds'] = int(d['clouds'])
            send = json.dumps(d)
            r = requests.post('https://monitoring.gpn.supply/api/contexts/1/weather-restrictions/' + 'addupdateparam', data=send,
                              headers=headers,
                              verify=False)
            # r=requests.post('https://localhost:44321/api/contexts/1/weather-restrictions/' + 'addupdateparam', data=send,
            #                    headers=headers,
            #                    verify=False)
            # print(r.content)

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
