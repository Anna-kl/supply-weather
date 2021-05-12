##########################################################################
# Copyright 2017 Curity AB
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##########################################################################
import configparser
import os
import json

class Config():


    def __init__(self, filename):
        self.filename = filename

    def load_config(self):
        self.config = configparser.ConfigParser()
        self.config.read('./config.ini')

    def red_access(self):
        str_con = {'url': self.config.get('TOKEN', 'url'),
                   'return_url': self.config.get('TOKEN', 'return_url'),
                   'username': self.config.get('TOKEN', 'username'),
                   'password': self.config.get('TOKEN', 'password')}
        return  str_con
    def read_db(self):

        str_con={'host':self.config.get('DATABASE','host'),
                 'user':self.config.get('DATABASE','user'),
                 'password': self.config.get('DATABASE', 'password'),
                 'port': '5432',
                 'api_key':self.config.get('WEATHER', 'api_key'),
                 'db':self.config.get('DATABASE', 'db')}
        return str_con

    def api_key(self):
        str_con={'api_key':self.config.get('WEATHER','api_key')}
        return str_con

