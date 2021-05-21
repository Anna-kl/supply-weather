FROM python:3

WORKDIR /usr/src/app
ENV api_key=48c910f8c4054b3cac5a84da4013c0d9
ENV URL = https://localhost:44321/api/weather-restrictions/
ENV access_token='test'
ENV url_server=https://localhost:44321/api/weather-restrictions/
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ /src
WORKDIR /src

CMD [ "python", "main.py" ]