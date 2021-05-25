import configparser
import sqlalchemy
import psycopg2
import json
import datetime
import os
import requests


class History:
    def __init__(self):
        self.api_key=os.environ['api_key']
        # self.connection()

        # url = 'postgresql://{}:{}@{}:{}/{}'
        # url = url.format(setting.login, setting.password, setting.host,
        #                  setting.port, setting.name)
        #
        # con = sqlalchemy.create_engine(url, echo=True)

    def get_data_hist(self, lat, lng, start_year, end_year, token, location):
        day_t=datetime.datetime.now().day

        year=start_year
        while(start_year<end_year):

            url = 'https://api.weatherbit.io/v2.0/history/daily?lat={0}&lon={1}&key={2}' \
              '&start_date={3}-05-0{4}&end_date={3}-05-{5}'.format(lat, lng, self.api_key,
                                                    start_year, day_t, day_t+1)
            r = requests.get(url)
            data = json.loads(r.content.decode())
            try:
             snow=0 if data['data'][0]['snow'] is None else data['data'][0]['snow']

             pres=0 if data['data'][0]['pres'] is None else data['data'][0]['pres']

             send =json.dumps({'restriction':'', 'warning':'', 'rh': data['data'][0]['rh'], 'temp': data['data'][0]['temp'], "locationId": location,
                    'pres': pres / 1.334, "wind_spd": data['data'][0]['wind_spd'],
                    "clouds": data['data'][0]['clouds'],
                    "lng": lng, "lat": lat, "snow": snow, 'vis': 0, 'dttm': data['data'][0]['datetime']. format(year, day_t)})

             headers = {'Authorization':
                           'Bearer {0}'.format(token),
                       'Content-type': 'application/json'}
             r = requests.post('https://localhost:44321/api/weather-restrictions/addparam', data=send, headers=headers,
                              verify=False)
            except Exception as ex:
                print(ex)
                return
            # print(r.content)
            # add=Weather_Param(rh=data['data'][0]['rh'], temp=data['data'][0]['temp'],
            #               pres=data['data'][0]['pres']/1.334, wind_spd=data['data'][0]['wind_spd'],
            #               clouds=data['data'][0]['clouds'], wind_gust_spd=data['data'][0]['wind_gust_spd'],
            #               locationids=1, lng=lng, lat=lat, snow=0, vis=0, dttm='{0}-05-0{1}'.format(start_year, day))
            #
            # session.add(add)
            start_year += 1
       # session.commit()






