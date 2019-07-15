#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging.config
# ==================== ------ STD LIBRARIES ------- ====================
import os
import pathlib
import sys
from typing import Dict
from typing import List

import common.PerformanceDatastructs.stats_datastruct as scores
from common.PerformanceDatastructs.clustermatch_datastruct import ClusterMatch
# ==================== ------ PERSONAL LIBRARIES ------- ====================
from common.environment_variable import get_homedir

sys.path.append(os.path.abspath(os.path.pardir))

# ==================== ------ PREPARATION ------- ====================
# load the logging configuration
logconfig_path = (get_homedir() / pathlib.Path("carlhauser_client", "logging.ini")).resolve()
logging.config.fileConfig(str(logconfig_path))


class ClusterMatchingQualityEvaluator:
    def __init__(self):
        # self.logger = logging.getLogger(__name__)
        pass

    @staticmethod
    def evaluate_performance(clusters_pairs: List[ClusterMatch], total_number_element=None) -> List[ClusterMatch]:
        '''
        Compute statistic about each cluster pairs, for them members. Check the True positive, False positive, etc. rates
        :param clusters_pairs: A list of pairs of clusters = [ (cluster1, clusterA), (cluster2, clusterB) ...)
        :param total_number_element: Total number of members (not the sum of all members of all clusters, but how many elements is there regardless of their classification) in the "world" considered.
        :return: The same List of pairs of cluster, but with the score set-up
        '''
        # Flush the internal memory of the evaluator and compute statistics over each clusters pair. Store means, etc. in internal memory.

        for pair in clusters_pairs:
            s = scores.Stats_datastruct()

            # Get members of both clusters
            truth_set = pair.cluster_1.members
            candidate_set = pair.cluster_2.members

            # Compute all values of the pair score
            s.compute_all(truth_set, candidate_set, total_number_element)

            # Store the score
            pair.score = s

        return clusters_pairs

    @staticmethod
    def export_as_json(clusters_with_perfs: List[ClusterMatch]) -> Dict:
        # Save performances results in a file as json (return the same structure)

        perfs = {"scores": [[str(e.cluster_1), str(e.cluster_2), str(e.score)] for e in clusters_with_perfs]}

        # Compute mean score (from the list of scores)
        total = scores.merge_scores([s.score for s in clusters_with_perfs])

        perfs["overview"] = vars(total)

        return perfs
