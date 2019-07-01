# ==================== ------ STD LIBRARIES ------- ====================
import os
import sys
from collections import namedtuple

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))

from carlhauser_server.Configuration.template_conf import JSON_parsable_Dict
from carlhauser_server.Helpers.environment_variable import get_homedir

class Default_webservice_conf(JSON_parsable_Dict):
    def __init__(self):
        # Please note that CERT and KEY files must be in carl-hauser/carlhauser_server (where the flask server is)
        self.CERT_FILE = get_homedir() / 'carlhauser_server' /'cert.pem' # './cert.pem'
        self.KEY_FILE = get_homedir() / 'carlhauser_server' / 'key.pem' # './key.pem'

def parse_from_dict(conf):
    return namedtuple("Default_webservice_conf", conf.keys())(*conf.values())





'''
# ==================== To string ====================

    # Overwrite to print the content of the cluster instead of the cluster memory address
    def __repr__(self):
        return self.get_str()

    def __str__(self):
        return self.get_str()

    def get_str(self):
        return ''.join(map(str, [' \nCERT_FILE=', self.CERT_FILE,
                                 ' \nKEY_FILE=', self.KEY_FILE]))
'''