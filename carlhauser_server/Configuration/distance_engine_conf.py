# ==================== ------ STD LIBRARIES ------- ====================

from enum import Enum, auto
import logging
import sys, os

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))
from carlhauser_server.Configuration.template_conf import FORMATTER as FORMATTER
from carlhauser_server.Configuration.template_conf import JSON_parsable_Enum, JSON_parsable_Dict


class Default_configuration(JSON_parsable_Dict):
    def __init__(self):
        # Inputs
        self.SOURCE_DIR = None

        '''
        self.GROUND_TRUTH_PATH = None
        self.IMG_TYPE = SUPPORTED_IMAGE_TYPE.PNG
        # Processing
        self.ALGO = ALGO_TYPE.A_HASH
        self.SELECTION_THREESHOLD = None #TODO : To fix and to use, to prevent "forced linked" if none
        # Threshold
        self.THREESHOLD_EVALUATION = THRESHOLD_MODE.MAXIMIZE_TRUE_POSITIVE
        # Output
        self.SAVE_PICTURE_INSTRUCTION_LIST = []
        self.OUTPUT_DIR = None
        '''