# ==================== ------ STD LIBRARIES ------- ====================

from enum import Enum, auto
import logging
import sys, os

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))
FORMATTER = logging.Formatter('%(asctime)s - + %(relativeCreated)d - %(name)s - %(levelname)s - %(message)s')

class X_MODES(Enum):
    X = auto()
    Y = auto()

class Default_configuration():
    def __init__(self):
        self.X = X_MODES.X
        self.Z = None

