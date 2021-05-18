
import hug
import jwt
import json
from hug_middleware_cors import CORSMiddleware
import requests
from jwt.algorithms import get_default_algorithms
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from urllib.parse import urlparse
import re
from config import Config
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
_congif=Config('/config.ini')
_congif.load_config()
conf=_congif.red_access()
data= {"Username": conf['username'],"Password": conf['password'], "RememberLogin": False,
     "ReturnUrl":conf['return_url']}
def get_token():
    r=requests.post(conf['url'],  verify=False, data=data)
    r=requests.get(r.url, verify=False)
    params = r.url.split('#')[1]
    d = dict(re.findall(r'([^=\&]*)=([^\&]*)', params))
    return d