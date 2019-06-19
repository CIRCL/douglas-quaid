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

class Default_database_conf(JSON_parsable_Dict):
    def __init__(self):
        # Please note that CERT and KEY files must be in carl-hauser/carlhauser_server (where the flask server is)
        self.DB_SCRIPTS_PATH = pathlib.Path('carlhauser_server', 'Helpers', 'database_scripts')
        self.DB_SOCKETS_PATH = pathlib.Path('carlhauser_server', 'Helpers', 'database_sockets')
        self.DB_DATA_PATH = pathlib.Path('carlhauser_server', 'Helpers', 'database_data')

        # Expiration time after which a add_request, computation_request, ... is removed (satisfied or not)
        self.REQUEST_EXPIRATION = 86400
        self.ANSWER_EXPIRATION = 86400

        # NB of worker on launch
        self.ADDER_WORKER_NB = 2
        self.ADDER_WAIT_SEC = 1

        # NB of worker on launch
        self.REQUESTER_WORKER_NB = 2
        self.REQUESTER_WAIT_SEC = 1

def parse_from_dict(conf):
    return namedtuple("Default_database_conf", conf.keys())(*conf.values())
