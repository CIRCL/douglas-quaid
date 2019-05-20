# ==================== ------ STD LIBRARIES ------- ====================

from enum import Enum, auto
import logging
import sys, os

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))
from carlhauser_server.Configuration.template_conf import FORMATTER as FORMATTER
from carlhauser_server.Configuration.template_conf import JSON_parsable_Enum, JSON_parsable_Dict


class Default_distance_engine_conf(JSON_parsable_Dict):
    def __init__(self):
        # Inputs
        self.TOP_N_CLUSTERS = 3 # Nb of "best clusters" to be matched on picture representative
        self.TOP_N_PICTURES = 10 # Nb of "best pictures" to be returned, from TOP_N_CLUSTERS best clusters (total, not per cluster)
        self.PICT_TO_TEST_PER_CLUSTER = 1 # Nb of "central picture" to test per cluster

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