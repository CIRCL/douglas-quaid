#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging.config
# ==================== ------ STD LIBRARIES ------- ====================
import os
import pathlib
import sys

from typing import List

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))
from carlhauser_client.Helpers.environment_variable import get_homedir
from common.Graph.cluster import Cluster
import carlhauser_client.Helpers.stats_datastruct as scores
import carlhauser_server.Helpers.json_import_export as json_import_export

# from . import helpers

# ==================== ------ PREPARATION ------- ====================
# load the logging configuration
logconfig_path = (get_homedir() / pathlib.Path("carlhauser_client", "logging.ini")).resolve()
logging.config.fileConfig(str(logconfig_path))

class ClusterMatchingQualityEvaluator():
    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Tmp storage
        self.clusters_with_perfs = []

    def flush_memory(self):
        self.clusters_with_perfs = []

    def evaluate_performance(self, clusters_pairs: List[List[Cluster]], total_number_element=None):
        # Flush the internal memory of the evaluator and compute statistics over each clusters pair. Store means, etc. in internal memory.

        self.flush_memory()

        for pair in clusters_pairs:

            s = scores.Stats_datastruct()

            # Get members of both clusters
            truth_set = pair[0].members
            candidate_set = pair[1].members

            # Compute all values of the pair score
            s.compute_all(truth_set, candidate_set, total_number_element)

            # Store the score
            pair.append(s)

        self.clusters_with_perfs = clusters_pairs

        return clusters_pairs

    def save_perf_results(self, save_path_perf : pathlib.Path):
        # Save performances results in a file as json (return the same structure)

        perfs = {"scores":[ [str(e[0]), str(e[1]), str(e[2]) ] for e in self.clusters_with_perfs]}

        # Compute mean score (from the list of scores)
        total = scores.merge_scores([s[2] for s in self.clusters_with_perfs])

        perfs["overview"] = vars(total)

        json_import_export.save_json(perfs, save_path_perf)
        self.logger.debug(f"Json saved in : {save_path_perf}")

        return total

