#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging.config
# ==================== ------ STD LIBRARIES ------- ====================
import os
import pathlib
import sys

import common.PerformanceDatastructs.stats_datastruct as scores
from common.Graph.cluster import Cluster
# ==================== ------ PERSONAL LIBRARIES ------- ====================
from common.environment_variable import get_homedir, JSON_parsable_Dict

sys.path.append(os.path.abspath(os.path.pardir))

# ==================== ------ PREPARATION ------- ====================
# load the logging configuration
logconfig_path = (get_homedir() / pathlib.Path("carlhauser_client", "logging.ini")).resolve()
logging.config.fileConfig(str(logconfig_path))


class ClusterMatch(JSON_parsable_Dict):
    def __init__(self, cluster1: Cluster, cluster2: Cluster):
        self.cluster_1: Cluster = cluster1
        self.cluster_2: Cluster = cluster2
        self.score: scores.Stats_datastruct = None
