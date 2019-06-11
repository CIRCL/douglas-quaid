# ==================== ------ STD LIBRARIES ------- ====================
from collections import namedtuple

from enum import Enum, auto
import logging
import sys, os
import pathlib

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))

from carlhauser_server.Configuration.template_conf import FORMATTER as FORMATTER
from carlhauser_server.Configuration.template_conf import JSON_parsable_Enum, JSON_parsable_Dict
from carlhauser_server.Helpers.environment_variable import get_homedir

class Default_webservice_conf(JSON_parsable_Dict):
    def __init__(self):
        # Please note that CERT and KEY files must be in carl-hauser/carlhauser_server (where the flask server is)
        self.CERT_FILE = get_homedir() / 'carlhauser_server' /'cert.pem' # './cert.pem'
        self.KEY_FILE = get_homedir() / 'carlhauser_server' / 'key.pem' # './key.pem'

def parse_from_dict(conf):
    return namedtuple("Default_webservice_conf", conf.keys())(*conf.values())
