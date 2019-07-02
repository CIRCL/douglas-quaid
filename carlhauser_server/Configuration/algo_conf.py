# ==================== ------ STD LIBRARIES ------- ====================
import os
import sys
from collections import namedtuple
from enum import Enum, auto
from typing import List

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))
from carlhauser_server.Configuration.template_conf import JSON_parsable_Enum, JSON_parsable_Dict


class Algo_conf(JSON_parsable_Dict):
    def __init__(self, algo_name: str, is_enabled: bool, threshold_maybe: float, threshold_no: float, distance_weight: float, decision_weight=None):
        self.algo_name: str = algo_name
        self.is_enabled: bool = is_enabled

        # Threshold for Y/M/N
        self.threshold_maybe: float = threshold_maybe  # Inclusive
        self.threshold_no: float = threshold_no  # Inclusive

        # Relative weight of this algorithm in merging phase
        self.distance_weight: float = distance_weight
        self.decision_weight: float = distance_weight if decision_weight is None else decision_weight

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
