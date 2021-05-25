import urllib.request
import json
from Models.Weather import Weather
from Models.History import History
import requests
from datetime import datetime, timedelta
url = 'https://api.weatherbit.io/v2.0/current?city=Tomsk&country=RU&key=48c910f8c4054b3cac5a84da4013c0d9&include=minutely'
req = urllib.request.Request(url)
import hug
import jwt
import json
from hug_middleware_cors import CORSMiddleware
import requests
import client

c=client.get_token()
m=Weather()
locations=m.get_location(c['access_token'])

h=History()
for loc in locations:
    if loc['latitude']!=0:
        h.get_data_hist(loc['latitude'], loc['longitude'], 2016, 2021,
                        c['access_token'], loc['id'])

for loc in locations:
    if loc['latitude'] != 0:
        data=m.get_data_forecast_day(loc['latitude'], loc['longitude'], 4, loc['id'])
        data=m.normalization(datetime.now(), data, c['access_token'], loc['id'])
        m.analize(data, datetime.now().date(), c['access_token'])



