#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
# ==================== ------ STD LIBRARIES ------- ====================
import os
import pathlib
import sys
import uuid
import os
import pathlib
import sys
import time
import traceback
import redis
import argparse

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))
from common.Graph.graph_datastructure import GraphDataStruct
from common.Graph.metadata import Metadata, Source
from common.Graph.cluster import Cluster
from common.Graph.edge import Edge
from common.Graph.node import Node

from carlhauser_server.Helpers.environment_variable import dir_path
import carlhauser_server.Helpers.json_import_export as json_import_export

import carlhauser_server.Configuration.database_conf as database_conf
import carlhauser_server.Configuration.distance_engine_conf as distance_engine_conf
import carlhauser_server.Configuration.feature_extractor_conf as feature_extractor_conf

import carlhauser_server.DatabaseAccessor.database_worker as database_accessor
import carlhauser_server.DistanceEngine.distance_engine as distance_engine
import carlhauser_server.DatabaseAccessor.database_utilities as db_utils
import carlhauser_server.DistanceEngine.scoring_datastrutures as scoring_datastrutures


class Database_Common(database_accessor.Database_Worker):
    def __init__(self, db_conf: database_conf, dist_conf: distance_engine_conf, fe_conf: feature_extractor_conf):
        # STD attributes
        super().__init__(db_conf)

        # Store configuration
        self.dist_conf = dist_conf
        self.fe_conf = fe_conf

        # Distance engine
        self.de = distance_engine.Distance_Engine(self, db_conf, dist_conf, fe_conf)
        self.db_utils = db_utils.DBUtilities(db_access_decode=self.storage_db_decode, db_access_no_decode=self.storage_db_no_decode)

    def _to_run_forever(self):
        # Method called infinitely, in loop

        # Trying to fetch from queue (to_add)
        fetched_id, fetched_dict = self.get_from_queue(self.cache_db_no_decode, self.input_queue, pickle=True)

        # If there is nothing fetched
        if not fetched_id:
            # Nothing to do
            time.sleep(0.1)
            return 0

        try:
            self.process_fetched_data(fetched_id, fetched_dict)

        except Exception as e:
            self.logger.error(f"Error in database accessors : {e}")
            self.logger.error(traceback.print_tb(e.__traceback__))

        return 1

    def process_fetched_data(self, fetched_id, fetched_dict):
        self.logger.error(f"'process_fetched_data' must be overwritten ! No action performed by this worker.")
