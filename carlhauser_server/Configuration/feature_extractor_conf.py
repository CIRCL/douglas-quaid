# ==================== ------ STD LIBRARIES ------- ====================
from collections import namedtuple
from enum import Enum, auto
import logging
import sys, os

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))
from carlhauser_server.Configuration.template_conf import FORMATTER as FORMATTER
from carlhauser_server.Configuration.template_conf import JSON_parsable_Enum, JSON_parsable_Dict


class Algo_conf(JSON_parsable_Dict):
    def __init__(self, is_enabled, threshold_maybe, threshold_no, weight):
        self.is_enabled = is_enabled

        # Threshold for Y/M/N
        self.threshold_maybe = threshold_maybe
        self.threshold_no = threshold_no

        # Relative weight of this algorithm in merging phase
        self.weight = weight


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
        self.A_HASH = Algo_conf(False, 0.2, 0.6, weight=1)
        self.P_HASH = Algo_conf(True, 0.2, 0.6, weight=1)
        self.P_HASH_SIMPLE = Algo_conf(False, 0.2, 0.6, weight=1)
        self.D_HASH = Algo_conf(True, 0.2, 0.6, weight=1)
        self.D_HASH_VERTICAL = Algo_conf(False, 0.2, 0.6, weight=1)
        self.W_HASH = Algo_conf(False, 0.2, 0.6, weight=1)
        self.TLSH = Algo_conf(True, 0.2, 0.6, weight=1)

        # Visual Descriptors parameters
        self.ORB = Algo_conf(True, 0.2, 0.6, weight=5)
        self.ORB_KEYPOINTS_NB = 500


def parse_from_dict(conf):
    return namedtuple("Default_feature_extractor_configuration", conf.keys())(*conf.values())
