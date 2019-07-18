#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import common.PerformanceDatastructs.stats_datastruct as scores
from common.environment_variable import JSON_parsable_Dict
from common.environment_variable import load_server_logging_conf_file
load_server_logging_conf_file()


class Perf(JSON_parsable_Dict):
    def __init__(self, score: scores.Stats_datastruct, threshold: float):
        self.score: scores.Stats_datastruct = score
        self.threshold: float = threshold

    # Overwrite to print the content of the cluster instead of the cluster memory address
    def __repr__(self):

        return self.get_str()

    def __str__(self):
        return self.get_str()

    def get_str(self):
        return ''.join(map(str, ['score=', self.score,
                                 ' threshold=', self.threshold]))

