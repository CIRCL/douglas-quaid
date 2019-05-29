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
from carlhauser_client.API.carlhauser_client import API_caller
from common.Graph.graph_datastructure import GraphDataStruct
from common.Graph.metadata import Metadata, Source
from common.Graph.cluster import Cluster
from common.Graph.edge import Edge
from common.Graph.node import Node
# from . import helpers
from pprint import pformat

# ==================== ------ PREPARATION ------- ====================
# load the logging configuration
logconfig_path = (get_homedir() / pathlib.Path("carlhauser_client", "logging.ini")).resolve()
logging.config.fileConfig(str(logconfig_path))


# ==================== ------ LAUNCHER ------- ====================

class Cluster_matcher():
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def match_clusters(self, original: List[Cluster], candidate: List[Cluster]):
        self.logger.debug(f"Inputs : \n original = {pformat(original)} \n original = {pformat(candidate)}")

        # Sort arrays (bigger to smaller)
        original.sort(key=lambda x: len(x.members), reverse=True)
        candidate.sort(key=lambda x: len(x.members), reverse=True)

        self.logger.debug(f"Sorted : \n original = {pformat(original)} \n original = {pformat(candidate)}")

        matching = []

        # Try to match
        for curr_original_cluster in original:
            max_intersect = 0
            index_best_intersect = -1

            for i, curr_candidat_cluster in enumerate(candidate):
                if len(curr_candidat_cluster.members) < max_intersect:
                    # The current cluster and the next one can't be better that already found matching

                    # Remove current cluster from matching
                    # TODO : if index_best_intersect != -1 :
                    #  candidate.remove(index_best_intersect)
                    # else :
                    # "No candidate found for ... "
                    if index_best_intersect == -1:
                        self.logger.debug(f"No candidate found to match {curr_original_cluster}")

                    break  # So we stop
                else:
                    # Compute intersection
                    tmp = len(curr_original_cluster.members.intersection(curr_candidat_cluster.members))

                    # Store if better
                    if tmp > max_intersect:
                        max_intersect = tmp
                        index_best_intersect = i

            # Store best matching
            matching.append([curr_original_cluster, candidate[index_best_intersect]])

        self.logger.debug(f"matching : \n {pformat(matching)}")

        return matching
        # TODO : Problem with clusters that are not matched.
        # What to do with them ? Let them ? Match them by force ? ...
