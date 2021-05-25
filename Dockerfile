FROM python:3

WORKDIR /usr/src/app
ENV api_key=48c910f8c4054b3cac5a84da4013c0d9
ENV URL = https://localhost:44321/api/weather-restrictions/
ENV access_token=test
ENV url_server=https://localhost:44321/api/weather-restrictions/
ENV Username=Anna
ENV Password=1234
ENV return_url=/connect/authorize/callback?client_id=js&redirect_uri=http://localhost:8080/callback.html&response_type=id_token_token&scope=openid_profile_api&state=23f0ba3409a7448aa3947e32f1dcf1c7&nonce=fea2160829a645e1ab2f2e8a9cc2b01b
ENV url_token=https://localhost:44375/Account/login/
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ /src
WORKDIR /src

CMD [ "python", "main.py" ]
