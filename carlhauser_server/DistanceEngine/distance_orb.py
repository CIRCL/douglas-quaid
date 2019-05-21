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


class Distance_ORB():
    def __init__(self, db_conf: database_conf, dist_conf: distance_engine_conf,  fe_conf: feature_extractor_conf):
        # STD attributes
        self.logger = logging.getLogger(__name__)
        self.logger.info("Creation of a Distance ORB Engine")

        # Save configuration
        self.db_conf = db_conf # TODO : REMOVE = NOT USEFUL FOR NOW !
        self.dist_conf = dist_conf
        self.fe_conf = fe_conf

        self.orb_matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=dist_conf.CROSSCHECK)

    def orb_distance(self, pic_package_from, pic_package_to):
        answer = {}
        self.logger.info("Orb distance computation ... ")

        try:
            # Note : @image must be a PIL instance.
            if self.fe_conf.ORB:
                # Compute matches
                matches = self.orb_matcher.match(pic_package_from["ORB_DESCRIPTORS"], pic_package_to["ORB_DESCRIPTORS"])

                answer["ORB_DISTANCE"] = self.max_dist(matches, self.threeshold_distance_filter(matches))

        except Exception as e:
            self.logger.error("Error during orbing : " + str(e))

        return answer

    def threeshold_distance_filter(self, matches):
        dist_th = 64
        good = []

        for curr_matches in matches:
            if curr_matches.distance < dist_th:
                good.append(curr_matches)

        return good

    def max_dist(self, all_matches, good_matches):
        return 1 - len(good_matches) / (max(len(all_matches), len(all_matches)))
