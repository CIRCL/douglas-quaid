#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==================== ------ STD LIBRARIES ------- ====================
import sys, os
import redis
import logging
import time
import argparse
import pathlib
import imagehash
import tlsh

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))

from carlhauser_server.Helpers.environment_variable import get_homedir, dir_path
import carlhauser_server.Helpers.json_import_export as json_import_export

import carlhauser_server.DatabaseAccessor.database_worker as database_accessor
import carlhauser_server.Configuration.database_conf as database_conf
import carlhauser_server.Configuration.feature_extractor_conf as feature_extractor_conf


class Picture_Hasher():
    def __init__(self, conf: feature_extractor_conf):
        # STD attributes
        self.conf = conf
        self.logger = logging.getLogger(__name__)
        self.logger.info("Creation of a Picture Hasher")

    def hash_picture(self, curr_picture):
        answer = {}

        try:
            if self.conf.A_HASH:
                answer["A_HASH"] = self.check_null_hash(imagehash.average_hash(curr_picture))
            if self.conf.P_HASH:
                answer["P_HASH"] = self.check_null_hash(imagehash.phash(curr_picture))
            if self.conf.P_HASH_SIMPLE:
                answer["P_HASH_SIMPLE"] = self.check_null_hash(imagehash.phash_simple(curr_picture))
            if self.conf.D_HASH:
                answer["D_HASH"] = self.check_null_hash(imagehash.dhash(curr_picture))
            if self.conf.D_HASH_VERTICAL:
                answer["D_HASH_VERTICAL"] = self.check_null_hash(imagehash.dhash_vertical(curr_picture))
            if self.conf.W_HASH:
                answer["W_HASH"] = self.check_null_hash(imagehash.whash(curr_picture))
            if self.conf.TLSH:
                answer["TLSH"] = self.check_null_hash(tlsh.hash(curr_picture))

        except Exception as e:
            self.logger.error("Error during hashing : " + str(e))

        return answer

    def check_null_hash(self, hash):
        # Check if the hash provided is null/None/empty. If yes, provide a default hash

        if not hash or hash is None or hash == "":
            return '0000000000000000000000000000000000000000000000000000000000000000000000'
        return hash
