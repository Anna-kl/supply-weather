import urllib.request
from Models.Weather import Weather
import os
url = 'https://api.weatherbit.io/v2.0/current?city=Tomsk&country=RU&key=48c910f8c4054b3cac5a84da4013c0d9&include' \
      '=minutely '
url_server = os.environ['url_server']
req = urllib.request.Request(url)

access=os.environ['access_token']
m = Weather()
send = m.get_data_forecast_day(56.4977, 84.9744, 3)
m.write_data(access, send)
