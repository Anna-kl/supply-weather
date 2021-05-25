import json
import requests
from urllib.parse import urlparse
import re
import os


myheaders={'Content-type':'application/json', 'Accept':'application/json'}
data= {"Username": os.environ['Username'],
       "Password": os.environ['password'], "RememberLogin": False,
     "ReturnUrl":os.environ['return_url']}

def get_token():
    params = {'button': 'login'}
    r=requests.post(os.environ['url_token'],  verify=False, data=data, params=params)
    r=requests.get(r.url, verify=False)
    r = requests.get(r.url, verify=False)
    params = r.url.split('#')[1]
    d = dict(re.findall(r'([^=\&]*)=([^\&]*)', params))
    return d
