# ==================== ------ STD LIBRARIES ------- ====================
from collections import namedtuple
from enum import Enum, auto
import logging
import sys, os

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))
from carlhauser_server.Configuration.template_conf import FORMATTER as FORMATTER
from carlhauser_server.Configuration.template_conf import JSON_parsable_Enum, JSON_parsable_Dict


# Used to export easily configuration to files, for logging
class Default_feature_extractor_conf(JSON_parsable_Dict):
    def __init__(self):
        # NB of worker on launch
        self.FEATURE_ADDER_WORKER_NB = 2
        self.FEATURE_ADDER_WAIT_SEC = 1

        # NB of worker on launch
        self.FEATURE_REQUEST_WORKER_NB = 2
        self.FEATURE_REQUEST_WAIT_SEC = 1

        # HASH parameters
        self.A_HASH = False
        self.P_HASH = True
        self.P_HASH_SIMPLE = False
        self.D_HASH = True
        self.D_HASH_VERTICAL = False
        self.W_HASH = False
        self.TLSH = True

        # Visual Descriptors parameters
        self.ORB = True
        self.ORB_KEYPOINTS_NB = 500


def parse_from_dict(conf):
    return namedtuple("Default_feature_extractor_configuration", conf.keys())(*conf.values())
