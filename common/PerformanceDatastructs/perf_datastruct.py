#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging.config
# ==================== ------ STD LIBRARIES ------- ====================
import os
import pathlib
import sys

import common.PerformanceDatastructs.stats_datastruct as scores
# ==================== ------ PERSONAL LIBRARIES ------- ====================
from common.environment_variable import get_homedir, JSON_parsable_Dict

sys.path.append(os.path.abspath(os.path.pardir))

# ==================== ------ PREPARATION ------- ====================
# load the logging configuration
logconfig_path = (get_homedir() / pathlib.Path("carlhauser_client", "logging.ini")).resolve()
logging.config.fileConfig(str(logconfig_path))


class Perf(JSON_parsable_Dict):
    def __init__(self, score: scores.Stats_datastruct, threshold: float):
        self.score: scores.Stats_datastruct = score
        self.threshold: float = threshold
