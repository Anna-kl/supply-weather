
import sqlalchemy
import json
import datetime

import requests

from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, MetaData, Integer, Computed,  DateTime
from sqlalchemy.orm import Session, sessionmaker

Base = declarative_base()


class History:
    def __init__(self):
       pass






    def get_data_hist(self, lat, lng, start_year, end_year):
        # Session = sessionmaker(self.con)
        # session=Session()
        day_t=datetime.datetime.now().day-2
        day_f = datetime.datetime.now().day + 2
        year=start_year
        while(start_year<end_year):
          day = day_t
          while day<=day_f:
            url = 'https://api.weatherbit.io/v2.0/history/daily?lat={0}&lon={1}&key={2}' \
              '&start_date={3}-05-0{4}&end_date={3}-05-{5}'.format(lat, lng, self.settings_base['api_key'],
                                                    start_year, day, day+1)
            r = requests.get(url)
            data = json.loads(r.content.decode())
            send =json.dumps({'restriction':'', 'warning':'', 'rh': data['data'][0]['rh'], 'temp': data['data'][0]['temp'], "LocationIds": 1,
                    'pres': data['data'][0]['pres'] / 1.334, "wind_spd": data['data'][0]['wind_spd'],
                    "clouds": data['data'][0]['clouds'],
                    "lng": lng, "lat": lat, "snow": data['data'][0]['snow'], 'vis': 0, 'dttm': data['data'][0]['datetime']. format(year, day)})

            headers = {'Authorization':
                           'Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IjlEM0YyNDA0MEQ2QUZCODdCQjhDMkNBQjMwOEU4OUQwNEUwQzhCOTYiLCJ0eXAiOiJhdCtqd3QiLCJ4NXQiOiJuVDhrQkExcS00ZTdqQ3lyTUk2SjBFNE1pNVkifQ.eyJuYmYiOjE2MjA5MDk4MTYsImV4cCI6MTYyMDkxMTYxNiwiaXNzIjoiaHR0cHM6Ly90ZXN0LmFjdHVhbC5zdXBwbHkiLCJhdWQiOiJhcGkiLCJjbGllbnRfaWQiOiJqcyIsInN1YiI6IjUyIiwiYXV0aF90aW1lIjoxNjIwOTA5ODE2LCJpZHAiOiJHb29nbGUiLCJzY29wZSI6WyJvcGVuaWQiLCJwcm9maWxlIiwiYXBpIl0sImFtciI6WyJleHRlcm5hbCJdfQ.bvEh7sSGvfbI3V2VqLfHYPuhzXLtshl0MMAn7j0TO48sVBnlCKJPcpguJJYNpiXeKwTO8imtOxa5_7ygVZn3CjcbnO7hGLW1MX3sygXhLbE1j1n5BL7hL__0yTKf6gjyuhSBp9sn4go4kxUVmgHi3mYezG-8uoH1IeDiO2orNpgs4GE5C8gBTU-yPvno0OIL5vzYZjJpkYM98JK7SCOGZAk9eiHbWt2TQnH5ZXbXvuf3KZX7IL_kRI5eXU_j2tZd-LEFPjRccbjrD3v3bn3CLu3XDd4ARO1JYP_6-UIVCcGOajg7Bv8CrqVrTaA0uALDf4n4PXVjWx_QvGXJnZ5Irw',
                       'Content-type': 'application/json'}
            r = requests.post('https://localhost:44321/api/weather-restrictions/addparam', data=send, headers=headers,
                              verify=False)

            print(r.content)


            day+=1
          start_year += 1
       # session.commit()



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


