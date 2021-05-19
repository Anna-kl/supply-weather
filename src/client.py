import requests

import re
from .Models import config

_congif = config.Config('/config.ini')
_congif.load_config()
conf = _congif.red_access()
data = {"Username": conf['username'], "Password": conf['password'], "RememberLogin": False,
        "ReturnUrl": conf['return_url']}


def get_token():
    r = requests.post(conf['url'], verify=False, data=data)
    r = requests.get(r.url, verify=False)
    params = r.url.split('#')[1]
    d = dict(re.findall(r'([^=&]*)=([^&]*)', params))
    return d
