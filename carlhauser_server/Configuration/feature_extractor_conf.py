# ==================== ------ STD LIBRARIES ------- ====================
import os
import sys
from collections import namedtuple
from enum import Enum, auto

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))
from carlhauser_server.Configuration.template_conf import JSON_parsable_Enum, JSON_parsable_Dict


class Distance_MergingMethod(JSON_parsable_Enum, Enum):
    MAX = auto()
    MEAN = auto()
    HARMONIC_MEAN = auto()
    MIN = auto()
    WEIGHTED_MEAN = auto()

class Decision_MergingMethod(JSON_parsable_Enum, Enum):
    PARETO = auto() # 80% Algo are the same
    MAJORITY = auto() # The most prevalent decision
    WEIGHTED_MAJORITY = auto() # The most prevalent decision, with weights
    PYRAMID = auto() # The most prevalent decision, if unsure, then look at lower ranked


class Algo_conf(JSON_parsable_Dict):
    def __init__(self, algo_name, is_enabled, threshold_maybe, threshold_no, distance_weight,  decision_weight=None):
        self.algo_name = algo_name
        self.is_enabled = is_enabled

        # Threshold for Y/M/N
        self.threshold_maybe = threshold_maybe # Inclusive
        self.threshold_no = threshold_no # Inclusive

        # Relative weight of this algorithm in merging phase
        self.distance_weight = distance_weight
        self.decision_weight = distance_weight if decision_weight is None else decision_weight

    # Addition to answer "as a dict" in tests files
    def get(self, attr_name, default=None):
        return getattr(self, attr_name, default)

    # ==================== To string ====================

    # Overwrite to print the content of the cluster instead of the cluster memory address
    def __repr__(self):
        return self.get_str()

    def __str__(self):
        return self.get_str()

    def get_str(self):
        return ''.join(map(str, [' algo_name=', self.algo_name,
                                 ' is_enabled=', self.is_enabled,
                                 ' threshold_maybe=', self.threshold_maybe,
                                 ' threshold_no=', self.threshold_no,
                                 ' distance_weight=', self.distance_weight,
                                 ' decision_weight=', self.decision_weight]))



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
        self.A_HASH = Algo_conf("A_HASH", False, 0.2, 0.6, distance_weight=1)
        self.P_HASH = Algo_conf("P_HASH", True, 0.2, 0.6, distance_weight=1)
        self.P_HASH_SIMPLE = Algo_conf("P_HASH_SIMPLE", False, 0.2, 0.6, distance_weight=1)
        self.D_HASH = Algo_conf("D_HASH", True, 0.2, 0.6, distance_weight=1)
        self.D_HASH_VERTICAL = Algo_conf("D_HASH_VERTICAL", False, 0.2, 0.6, distance_weight=1)
        self.W_HASH = Algo_conf("W_HASH", False, 0.2, 0.6, distance_weight=1)
        self.TLSH = Algo_conf("TLSH", True, 0.2, 0.6, distance_weight=1)

        # Visual Descriptors parameters
        self.ORB = Algo_conf("ORB", True, 0.2, 0.6, distance_weight=5)
        self.ORB_KEYPOINTS_NB = 500

        # Algo list # BEAWARE THAT
        # IF YOU MODIFY PROGRAMMATICALLY ONE ELEMENT LATER, YOU NEED TO CHANGE IT IN THIS LIST TOO !
        self.list_algos = [self.A_HASH, self.P_HASH, self.P_HASH_SIMPLE,
                           self.D_HASH, self.D_HASH_VERTICAL, self.W_HASH,
                           self.TLSH,
                           self.ORB]

        # Merging method
        self.DISTANCE_MERGING_METHOD = Distance_MergingMethod.WEIGHTED_MEAN.name
        self.DECISION_MERGING_METHOD = Decision_MergingMethod.WEIGHTED_MAJORITY.name

    '''
    # ==================== To string ====================

    # Overwrite to print the content of the cluster instead of the cluster memory address
    def __repr__(self):
        return self.get_str()

    def __str__(self):
        return self.get_str()

    def get_str(self):
        return ''.join(map(str, [' \nFEATURE_ADDER_WORKER_NB=', self.FEATURE_ADDER_WORKER_NB,
                                 ' \nFEATURE_ADDER_WAIT_SEC=', self.FEATURE_ADDER_WAIT_SEC,
                                 ' \nFEATURE_REQUEST_WORKER_NB=', self.FEATURE_REQUEST_WORKER_NB,
                                 ' \nFEATURE_REQUEST_WAIT_SEC=', self.FEATURE_REQUEST_WAIT_SEC,
                                 ' \nA_HASH=', self.A_HASH,
                                 ' \nP_HASH=', self.P_HASH,
                                 ' \nP_HASH_SIMPLE=', self.P_HASH_SIMPLE,
                                 ' \nD_HASH=', self.D_HASH,
                                 ' \nD_HASH_VERTICAL=', self.D_HASH_VERTICAL,
                                 ' \nW_HASH=', self.W_HASH,
                                 ' \nTLSH=', self.TLSH,
                                 ' \nORB=', self.ORB,
                                 ' \nORB_KEYPOINTS_NB=', self.ORB_KEYPOINTS_NB,
                                 ' \nTLSH=', self.TLSH,
                                 ' \nDISTANCE_MERGING_METHOD=', self.DISTANCE_MERGING_METHOD,
                                 ' \nDECISION_MERGING_METHOD=', self.DECISION_MERGING_METHOD]))

    '''

def parse_from_dict(conf):
    return namedtuple("Default_feature_extractor_configuration", conf.keys())(*conf.values())
