#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging.config
# ==================== ------ STD LIBRARIES ------- ====================
import os
import pathlib
import sys

from typing import List
from pprint import pformat

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))
from carlhauser_client.Helpers.environment_variable import get_homedir
from common.Graph.graph_datastructure import GraphDataStruct
from common.Graph.metadata import Metadata, Source
from common.Graph.cluster import Cluster
from common.Graph.edge import Edge
from common.Graph.node import Node
from carlhauser_client.Evaluator.scores import Scoring

# from . import helpers

# ==================== ------ PREPARATION ------- ====================
# load the logging configuration
logconfig_path = (get_homedir() / pathlib.Path("carlhauser_client", "logging.ini")).resolve()
logging.config.fileConfig(str(logconfig_path))

class Performance_Evaluator():
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def evaluate_performance(self, clusters_pairs: List[List[Cluster]], total_number_element=None):

        for pair in clusters_pairs:

            s = Scoring()

            truth_set = pair[0].members
            candidate_set = pair[1].members

            # Get number of "true element" in the dataset
            s.P = len(truth_set)

            # Compute true positive as intersection of ground truth and candidate clusters
            intersect = truth_set.intersection(candidate_set)
            s.TP = len(intersect)

            # Compute False Positive as what is in candidate but not in ground truth (and so the intersection)
            only_in_candidate = candidate_set.difference(intersect)
            s.FP = len(only_in_candidate)

            # Compute False Negative as what is in ground truth but not in candidate (and so the intersection)
            only_in_ground_truth = truth_set.difference(intersect)
            s.FN = len(only_in_ground_truth)

            # Diverse other metrics
            s.compute_TPR()
            s.compute_PPV()
            s.compute_FDR()

            if total_number_element is None:
                self.logger.warning("Can't compute True Negative rate : we don't know number of all elements in the system.")
            else:
                # Compute True negative as all elements not in the three previous sets
                s.TN = total_number_element - s.TP - s.FP - s.FN

                # Compute number of negative elements in dataset
                s.N = total_number_element - len(truth_set)

                # Diverse other metrics
                s.compute_TNR()
                s.compute_NPV()

                s.compute_FNR()
                s.compute_FPR()

                s.compute_FOR()

                s.compute_ACC()
                s.compute_F1()

            s.check_sanity()
            pair.append(s)

        return clusters_pairs
