# ==================== ------ STD LIBRARIES ------- ====================

from enum import Enum, auto
import logging
import sys, os

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))

from carlhauser_server.Configuration.template_conf import FORMATTER as FORMATTER

class X_MODES(Enum):
    X = auto()
    Y = auto()

class Default_webservice_conf():
    def __init__(self):
        self.X = X_MODES.X
        self.Z = None