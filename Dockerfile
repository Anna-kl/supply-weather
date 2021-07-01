FROM python:3

WORKDIR /usr/src/app
ENV api_key=48c910f8c4054b3cac5a84da4013c0d9
ENV URL = https://monitoring.gpn.supply/api/weather-restrictions/
ENV URL_Locations = https://monitoring.gpn.supply/api/locations/list
ENV access_token=test
ENV url_server=https://monitoring.gpn.supply/api/weather-restrictions/
ENV Username=Anna
ENV Password=1234
ENV return_url=/connect/authorize/callback?client_id=js&redirect_uri=https://monitoring.gpn.supply/callback.html&response_type=id_token token&scope=openid profile api&state=4ed6893afaf744fe9cfd6663a670adf0&nonce=304a3e4804db4966872e6a9d4e07f005
ENV url_token=https://core.gpn.supply/Account/Login/
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ /src
WORKDIR /src

CMD [ "python", "main.py" ]
