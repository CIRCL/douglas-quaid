# ==================== ------ STD LIBRARIES ------- ====================

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