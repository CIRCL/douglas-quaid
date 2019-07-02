# ==================== ------ STD LIBRARIES ------- ====================

from enum import Enum, auto
import logging
import sys, os

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))
FORMATTER = logging.Formatter('%(asctime)s - + %(relativeCreated)d - %(name)s - %(levelname)s - %(message)s')

# Both clases are used by a custom parser to import/export JSON
class JSON_parsable_Enum:
    pass

class JSON_parsable_Dict:
    pass

class X_MODES(JSON_parsable_Enum, Enum):
    X = auto()
    Y = auto()

class Default_configuration(JSON_parsable_Dict):
    def __init__(self):
        self.X = X_MODES.X
        self.Z = None
