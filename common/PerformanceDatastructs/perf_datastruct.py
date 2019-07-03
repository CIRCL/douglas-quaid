#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging.config
# ==================== ------ STD LIBRARIES ------- ====================
import os
import pathlib
import sys

from typing import List, Set

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))
from common.environment_variable import get_homedir
import common.PerformanceDatastructs.stats_datastruct as scores
from carlhauser_server.Configuration.template_conf import JSON_parsable_Dict

# from . import helpers

# ==================== ------ PREPARATION ------- ====================
# load the logging configuration
logconfig_path = (get_homedir() / pathlib.Path("carlhauser_client", "logging.ini")).resolve()
logging.config.fileConfig(str(logconfig_path))


class Perf(JSON_parsable_Dict):
    def __init__(self, score: scores.Stats_datastruct, threshold: float):
        self.score : scores.Stats_datastruct = score
        self.threshold  : float = threshold

