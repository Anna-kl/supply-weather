import urllib.request
from .Models.Weather import Weather

url = 'https://api.weatherbit.io/v2.0/current?city=Tomsk&country=RU&key=48c910f8c4054b3cac5a84da4013c0d9&include' \
      '=minutely '
req = urllib.request.Request(url)
from .client import get_token

access = get_token()

m = Weather()
send = m.get_data_forecast_day(56.4977, 84.9744, 3)
m.write_data(access['access_token'], send)
