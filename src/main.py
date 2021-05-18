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
from jwt.algorithms import get_default_algorithms
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from urllib.parse import urlparse
import re
import client


access=client.get_token()

m=Weather()
send=m.get_data_forecast_day(56.4977, 84.9744, 3)
m.write_data(access['access_token'], send)
