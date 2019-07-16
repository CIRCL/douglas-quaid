#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import common.PerformanceDatastructs.stats_datastruct as scores
from common.Graph.cluster import Cluster
from common.environment_variable import JSON_parsable_Dict
from common.environment_variable import load_server_logging_conf_file

load_server_logging_conf_file()


class ClusterMatch(JSON_parsable_Dict):
    def __init__(self, cluster1: Cluster, cluster2: Cluster):
        self.cluster_1: Cluster = cluster1
        self.cluster_2: Cluster = cluster2
        self.score: scores.Stats_datastruct = None
