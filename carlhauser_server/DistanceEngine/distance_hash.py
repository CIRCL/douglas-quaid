#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==================== ------ STD LIBRARIES ------- ====================
import sys, os
import imagehash
import tlsh
import cv2
import logging
# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))

import carlhauser_server.Configuration.database_conf as database_conf
import carlhauser_server.Configuration.distance_engine_conf as distance_engine_conf
import carlhauser_server.Configuration.feature_extractor_conf as feature_extractor_conf

import carlhauser_server.DatabaseAccessor.database_worker as database_accessor


class Distance_Hash():
    def __init__(self, db_conf: database_conf, dist_conf: distance_engine_conf,  fe_conf: feature_extractor_conf):
        # STD attributes
        self.logger = logging.getLogger(__name__)
        self.logger.info("Creation of a Distance Hash Engine")

        # Save configuration
        self.db_conf = db_conf # TODO : REMOVE = NOT USEFUL FOR NOW !
        self.dist_conf = dist_conf
        self.fe_conf = fe_conf

    # ==================== ------ INTER ALGO DISTANCE ------- ====================

    def hash_distance(self, pic_package_from, pic_package_to):
        answer = {}
        self.logger.info("Hash distance computation ... ")

        try:
            if self.fe_conf.A_HASH:
                self.logger.debug("A-HASH ... ")
                answer["A_HASH"] = self.compute_hash_distance(pic_package_from["A_HASH"], pic_package_to["A_HASH"])
            if self.fe_conf.P_HASH:
                self.logger.debug("P_HASH ... ")
                answer["P_HASH"] = self.compute_hash_distance(pic_package_from["P_HASH"], pic_package_to["P_HASH"])
            if self.fe_conf.P_HASH_SIMPLE:
                self.logger.debug("P_HASH_SIMPLE ... ")
                answer["P_HASH_SIMPLE"] = self.compute_hash_distance(pic_package_from["P_HASH_SIMPLE"], pic_package_to["P_HASH_SIMPLE"])
            if self.fe_conf.D_HASH:
                self.logger.debug("D_HASH ... ")
                answer["D_HASH"] = self.compute_hash_distance(pic_package_from["D_HASH"], pic_package_to["D_HASH"])
            if self.fe_conf.D_HASH_VERTICAL:
                self.logger.debug("D_HASH_VERTICAL ... ")
                answer["D_HASH_VERTICAL"] = self.compute_hash_distance(pic_package_from["D_HASH_VERTICAL"], pic_package_to["D_HASH_VERTICAL"])
            if self.fe_conf.W_HASH:
                self.logger.debug("W_HASH ... ")
                answer["W_HASH"] = self.compute_hash_distance(pic_package_from["W_HASH"], pic_package_to["W_HASH"])
            if self.fe_conf.TLSH:
                self.logger.debug("TLSH ... ")
                answer["TLSH"] = self.compute_tlsh_distance(pic_package_from["TLSH"], pic_package_to["TLSH"])

        except Exception as e:
            self.logger.error("Error during distance computation : " + str(e))

        return answer

    def compute_hash_distance(self, hash1, hash2):
        #TODO : Check if the size if accessible. Probably not.
        return abs(hash1 - hash2) / (hash1.hash.hash.size * 4)

    def compute_tlsh_distance(self, hash1, hash2):
        return tlsh.diff(hash1, hash2) / (len(hash1))
