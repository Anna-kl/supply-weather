import urllib.request
import json
from Models.Weather import Weather
from Models.History import History
import requests
from datetime import datetime, timedelta
import json
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



