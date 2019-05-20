#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==================== ------ STD LIBRARIES ------- ====================
import sys, os
import redis
import logging
import time
import argparse
import pathlib

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))

from carlhauser_server.Helpers.environment_variable import get_homedir, dir_path
import carlhauser_server.Helpers.json_import_export as json_import_export

import carlhauser_server.Helpers.database_start_stop as database_start_stop
import carlhauser_server.Configuration.database_conf as database_conf
import carlhauser_server.Configuration.distance_engine_conf as distance_engine_conf

import carlhauser_server.DatabaseAccessor.database_worker as database_accessor


class Distance_Engine(database_accessor.Database_Worker):
    def __init__(self, db_conf: database_conf, dist_conf: distance_engine_conf):
        super().__init__(db_conf)
        self.dist_conf = dist_conf
