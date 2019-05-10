# ==================== ------ STD LIBRARIES ------- ====================

from enum import Enum, auto
import logging
import sys, os

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))
from carlhauser_server.Configuration.template_conf import FORMATTER as FORMATTER

# Used to export easily configuration to files, for logging
class JSON_parsable_Enum():
    pass

class JSON_parsable_Dict():
    pass

class Default_configuration():
    def __init__(self):
        # Inputs
        self.SOURCE_DIR = None
