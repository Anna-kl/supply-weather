import requests
import re
from .Models import config

_congif = config.Config('/config.ini')
_congif.load_config()
conf = _congif.red_access()
data = {"Username": conf['username'], "Password": conf['password'], "RememberLogin": False,
        "ReturnUrl": conf['return_url']}


def get_token():
    r_url = requests.post(conf['url'], verify=False, data=data)
    r_url = requests.get(r_url.url, verify=False)
    params = r_url.url.split('#')[1]
    d = dict(re.findall(r'([^=&]*)=([^&]*)', params))
    return d
