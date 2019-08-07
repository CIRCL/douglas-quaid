from collections import namedtuple
from enum import Enum, auto
from typing import List
import pathlib

from carlhauser_server.Configuration.algo_conf import Algo_conf
from common.environment_variable import JSON_parsable_Enum, JSON_parsable_Dict
from common.environment_variable import get_homedir

class Distance_MergingMethod(JSON_parsable_Enum, Enum):
    MAX = auto()
    MEAN = auto()
    HARMONIC_MEAN = auto()
    MIN = auto()
    WEIGHTED_MEAN = auto()


class Decision_MergingMethod(JSON_parsable_Enum, Enum):
    PARETO = auto()  # 80% Algo are the same
    MAJORITY = auto()  # The most prevalent decision
    WEIGHTED_MAJORITY = auto()  # The most prevalent decision, with weights
    PYRAMID = auto()  # The most prevalent decision, if unsure, then look at lower ranked


# Used to export easily configuration to files, for logging
class Default_feature_extractor_conf(JSON_parsable_Dict):
    def __init__(self):
        # NB of worker on launch
        self.FEATURE_ADDER_WORKER_NB: int = 2
        self.FEATURE_ADDER_WAIT_SEC: int = 1

        # NB of worker on launch
        self.FEATURE_REQUEST_WORKER_NB: int = 2
        self.FEATURE_REQUEST_WAIT_SEC: int = 1

        # HASH parameters
        self.A_HASH: Algo_conf = Algo_conf("A_HASH", False, 0.02, 0.08, distance_weight=1)
        self.P_HASH: Algo_conf = Algo_conf("P_HASH", False, 0.08, 0.08, distance_weight=1) # True
        self.P_HASH_SIMPLE: Algo_conf = Algo_conf("P_HASH_SIMPLE", False, 0.04, 0.06, distance_weight=1)
        self.D_HASH: Algo_conf = Algo_conf("D_HASH", False, 0.04, 0.08, distance_weight=1) # True
        self.D_HASH_VERTICAL: Algo_conf = Algo_conf("D_HASH_VERTICAL", False, 0.04, 0.04, distance_weight=1)
        self.W_HASH: Algo_conf = Algo_conf("W_HASH", False, 0.06, 0.08, distance_weight=1)
        self.TLSH: Algo_conf = Algo_conf("TLSH", False, 0.16, 0.18, distance_weight=1) # True

        # Visual Descriptors parameters
        self.ORB: Algo_conf = Algo_conf("ORB", False, 0.0, 0.2, distance_weight=5) # True
        self.ORB_KEYPOINTS_NB: int = 500

        self.BOW_ORB : Algo_conf = Algo_conf("BOW_ORB", True, 0.08, 0.32, distance_weight=5) # True
        self.BOW_VOCAB_PATH : pathlib.Path = get_homedir() / "vocab.npy"

        # Algo list # /! IMPORTANT !\ BE-AWARE THAT /! IMPORTANT !\
        # IF YOU MODIFY PROGRAMMATICALLY ONE ELEMENT LATER, YOU NEED TO CHANGE IT IN THIS LIST TOO !
        self.list_algos: List[Algo_conf] = [self.A_HASH, self.P_HASH, self.P_HASH_SIMPLE,
                                            self.D_HASH, self.D_HASH_VERTICAL, self.W_HASH,
                                            self.TLSH,
                                            self.ORB,
                                            self.BOW_ORB]

        # Merging method
        self.DISTANCE_MERGING_METHOD: Distance_MergingMethod = Distance_MergingMethod.WEIGHTED_MEAN.name
        self.DECISION_MERGING_METHOD: Decision_MergingMethod = Decision_MergingMethod.WEIGHTED_MAJORITY.name

    '''
    [
    {
        "algo_name": "A_HASH",
        "is_enabled": true,
        "threshold_yes_to_maybe": 0.08,
        "threshold_maybe_to_no": 0.14,
        "distance_weight": 1,
        "decision_weight": 1
    },
    {
        "algo_name": "P_HASH",
        "is_enabled": true,
        "threshold_yes_to_maybe": 0.1,
        "threshold_maybe_to_no": 0.14,
        "distance_weight": 1,
        "decision_weight": 1
    }, (...)
    '''


def calibrated_algos_to_conf_file(calibrated_algos: List[Algo_conf]) -> Default_feature_extractor_conf:
    basic_conf = Default_feature_extractor_conf()

    # Create a dict (algo_name => algo_conf)
    algo_name_to_conf = {}
    for curr_calibrated_algo in calibrated_algos:
        algo_name_to_conf[curr_calibrated_algo.algo_name] = curr_calibrated_algo

    # Replace algo conf (if exists ! )
    basic_conf.A_HASH = algo_name_to_conf.get("A_HASH", basic_conf.A_HASH)
    basic_conf.P_HASH = algo_name_to_conf.get("P_HASH", basic_conf.P_HASH)
    basic_conf.P_HASH_SIMPLE = algo_name_to_conf.get("P_HASH_SIMPLE", basic_conf.P_HASH_SIMPLE)
    basic_conf.D_HASH = algo_name_to_conf.get("D_HASH", basic_conf.D_HASH)
    basic_conf.D_HASH_VERTICAL = algo_name_to_conf.get("D_HASH_VERTICAL", basic_conf.D_HASH_VERTICAL)
    basic_conf.W_HASH = algo_name_to_conf.get("W_HASH", basic_conf.W_HASH)
    basic_conf.TLSH = algo_name_to_conf.get("TLSH", basic_conf.TLSH)

    # Visual Descriptors parameters
    basic_conf.ORB = algo_name_to_conf.get("ORB", basic_conf.ORB)
    # TODO : add this parameter to calibrator ? basic_conf.ORB_KEYPOINTS_NB: int = 500

    # Reconstruct the list of algorithms
    basic_conf.list_algos: List[Algo_conf] = [basic_conf.A_HASH, basic_conf.P_HASH, basic_conf.P_HASH_SIMPLE,
                                              basic_conf.D_HASH, basic_conf.D_HASH_VERTICAL, basic_conf.W_HASH,
                                              basic_conf.TLSH,
                                              basic_conf.ORB]

    return basic_conf


def parse_from_dict(conf):
    tmp_conf = Default_feature_extractor_conf()
    tmp_conf.__dict__.update(conf)
    # Or : tmp_conf.__dict__ = conf

    return tmp_conf
    # return namedtuple("Default_feature_extractor_configuration", conf.keys())(*conf.values())


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
