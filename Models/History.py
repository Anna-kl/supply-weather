import configparser
import sqlalchemy
import psycopg2
import json

from sklearn import preprocessing
import requests
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, MetaData, Integer, Computed,  DateTime
from sqlalchemy.orm import Session, sessionmaker


Base = declarative_base()


class History:
    def __init__(self):
        self.connection()

        # url = 'postgresql://{}:{}@{}:{}/{}'
        # url = url.format(setting.login, setting.password, setting.host,
        #                  setting.port, setting.name)
        #
        # con = sqlalchemy.create_engine(url, echo=True)



    def connection(self):
        url = 'postgresql://{}:{}@{}:{}/{}'
        self.settings_base=self.read_config()
        url = url.format(self.settings_base['user'], self.settings_base['password'],
                         self.settings_base['host'],
                         self.settings_base['port'], self.settings_base['db'])

        # The return value of create_engine() is our connection object
        self.con = sqlalchemy.create_engine(url, client_encoding='utf8')
        self.meta = sqlalchemy.MetaData(bind=self.con,  schema='public')
        self.meta.create_all()

    def get_data_hist(self, lat, lng, start_year, end_year):
        Session = sessionmaker(self.con)
        session=Session()
        day_t=start_year.day-2
        year=start_year.year
        while(start_year<end_year):
          day = day_t
          while day<=9:
            url = 'https://api.weatherbit.io/v2.0/history/daily?lat={0}&lon={1}&key={2}' \
              '&start_date={3}-05-0{4}&end_date={3}-05-0{5}'.format(lat, lng, self.settings_base['api_key'],
                                                    year, day, day+1)
            r = requests.get(url)
            data = json.loads(r.content.decode())
            send =json.dumps({'rh': data['data'][0]['rh'], 'temp': data['data'][0]['temp'], "LocationIds": 1,
                    'pres': data['data'][0]['pres'] / 1.334, "wind_spd": data['data'][0]['wind_spd'],
                    "clouds": data['data'][0]['clouds'],
                    "lng": lng, "lat": lat, "snow": 0, 'vis': 0, 'dttm': "{0}-05-0{1}". format(year, day)})

            headers = {'Authorization':
                           'Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IjlEM0YyNDA0MEQ2QUZCODdCQjhDMkNBQjMwOEU4OUQwNEUwQzhCOTYiLCJ0eXAiOiJhdCtqd3QiLCJ4NXQiOiJuVDhrQkExcS00ZTdqQ3lyTUk2SjBFNE1pNVkifQ.eyJuYmYiOjE2MjA0ODc3OTEsImV4cCI6MTYyMDQ4OTU5MSwiaXNzIjoiaHR0cHM6Ly90ZXN0LmFjdHVhbC5zdXBwbHkiLCJhdWQiOiJhcGkiLCJjbGllbnRfaWQiOiJqcyIsInN1YiI6IjUyIiwiYXV0aF90aW1lIjoxNjIwNDgyNDU2LCJpZHAiOiJHb29nbGUiLCJzY29wZSI6WyJvcGVuaWQiLCJwcm9maWxlIiwiYXBpIl0sImFtciI6WyJleHRlcm5hbCJdfQ.GYbLTsyshr3GUmjMUJ2czs7vWtDpPidPbrodPLDkaFZWzLqkxhjhVmfxw7t4MMwFGP3YIGobIiCKewZ5TJPEqQcxwNyQqTSK2bHlUv3-MVcyGf9gzzErEAKHOWtLhjp4gGnv6tANThAB4oJI1o5xg75XRLbs8LMN8oL1E4C2mHhJuz0zyIs8B03xsRFwo_yul5PQUzVRL_mA52QwE7ZNhFgcK6XoNhtd4PP3TtcT9x-1Ck7vwzzx15VaaIoD7LZKNjOijb5yviMyLJmZ4cVMVEUNKv_smLknLQ9Ji_PcQotwywzYzXxNpDVLKnVHIj9SOY4XNM_sgDkqZoih_eHh-g',
                       'Content-type': 'application/json'}
            r = requests.post('https://localhost:44321/api/weather-restrictions/addparam', data=send, headers=headers,
                              verify=False)

            print(r.content)
            # add=Weather_Param(rh=data['data'][0]['rh'], temp=data['data'][0]['temp'],
            #               pres=data['data'][0]['pres']/1.334, wind_spd=data['data'][0]['wind_spd'],
            #               clouds=data['data'][0]['clouds'], wind_gust_spd=data['data'][0]['wind_gust_spd'],
            #               locationids=1, lng=lng, lat=lat, snow=0, vis=0, dttm='{0}-05-0{1}'.format(start_year, day))
            #
            # session.add(add)

            day+=1
          start_year += 1
        session.commit()



# history=History()
# con=history.read_config()
# db_string = "postgres://{0}:{1}@{2}:{3}/{4}".format(con['user'],con['password'],
#                                                     con['host'],con['port'], con['db'])
#
# db = create_engine(db_string)
#
# meta = MetaData(db)

class Weather_Param(Base):
    __tablename__='weather_params'
    id=Column(Integer, primary_key=True)
    wind_gust_spd=Column(DOUBLE_PRECISION)
    dttm=Column(DateTime)
    locationids=Column(Integer)
    lng=Column(DOUBLE_PRECISION)
    lat=Column(DOUBLE_PRECISION)
    vis=Column(DOUBLE_PRECISION)
    rh=Column(DOUBLE_PRECISION)
    clouds=Column(Integer)
    snow=Column(Integer)
    pres=Column(DOUBLE_PRECISION)
    wind_spd=Column(DOUBLE_PRECISION)
    temp=Column(DOUBLE_PRECISION)


