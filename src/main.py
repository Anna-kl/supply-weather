
from datetime import datetime, timedelta

from src import client
from src.Models.Weather import Weather


def get_weather():
    c=client.get_token()
    m=Weather()
    locations=m.get_location(c['access_token'])

    for loc in locations:
        if (loc['type'] == 'Route' or loc['type'] == 'Navigation') and loc['description'] != '':
            data = m.get_data_forecast_day_route(loc['description'], 4, loc['id'])
            all_data = m.analitics_weather_route(data,  c['access_token'])
        elif (loc['latitude'] != 0.0 and loc['latitude'] != None)\
                and (loc['type'] != 'Route' or loc['type'] != 'Navigation'):
            data = m.get_data_forecast_day(loc['latitude'], loc['longitude'], 4, loc['id'])
            data = m.normalization(datetime.now(), data, c['access_token'], loc['id'])
            m.analize(data, datetime.now().date(), c['access_token'])


