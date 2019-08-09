#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import logging
import traceback
from typing import Dict

import cv2

import carlhauser_server.Configuration.database_conf as database_conf
import carlhauser_server.Configuration.distance_engine_conf as distance_engine_conf
import carlhauser_server.Configuration.feature_extractor_conf as feature_extractor_conf
import carlhauser_server.DistanceEngine.scoring_datastrutures as sd
from carlhauser_server.Configuration.algo_conf import Algo_conf
from carlhauser_server.DistanceEngine.distance_hash import Distance_Hash as dist_hash
from common.CustomException import AlgoFeatureNotPresentError


class Distance_BoW_ORB:
    def __init__(self, db_conf: database_conf.Default_database_conf, dist_conf: distance_engine_conf.Default_distance_engine_conf, fe_conf: feature_extractor_conf.Default_feature_extractor_conf):
        # STD attributes
        self.logger = logging.getLogger(__name__)
        self.logger.info("Creation of a Distance ORB Engine")

        # Save configuration
        self.db_conf = db_conf  # TODO : REMOVE = NOT USEFUL FOR NOW !
        self.dist_conf = dist_conf
        self.fe_conf = fe_conf

        # TODO :
        self.orb_matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=dist_conf.CROSSCHECK)

    def bow_orb_distance(self, pic_package_from: Dict, pic_package_to: Dict) -> Dict[str, sd.AlgoMatch]:
        """
        Distance between two provided pictures (dicts) with BoW-ORB methods
        :param pic_package_from: first picture dict
        :param pic_package_to: second picture dict
        :return: A dictionary of algo name to the match detail (distance, decision ..)
        """

        answer = {}
        self.logger.info("BoW-Orb distance computation ... ")

        # Verify if what is needed to compute it is present
        if pic_package_from.get("BOW_ORB_DESCRIPTOR", None) is None \
                or pic_package_to.get("BOW_ORB_DESCRIPTOR", None) is None:
            self.logger.warning(f"BoW-ORB descriptors are NOT presents in the results : {pic_package_from} {pic_package_to}")
            raise AlgoFeatureNotPresentError("None BoW-ORB descriptors in orb distance.")

        # Add result for enabled algorithms
        try:
            if self.fe_conf.BOW_ORB.get("is_enabled", False):
                answer = self.add_results(self.fe_conf.BOW_ORB, pic_package_from, pic_package_to, answer)

        except Exception as e:
            self.logger.error(traceback.print_tb(e.__traceback__))
            self.logger.error("Error during bow-orb distance calculation : " + str(e))

        return answer

    def add_results(self, algo_conf: Algo_conf, pic_package_from: Dict, pic_package_to: Dict, answer: Dict) -> Dict:
        """
        Add results to answer dict, depending on the algorithm name we want to compute
        Ex : Input {} -> Output {"BOW_ORB":{"name":"BOW_ORB", "distance":0.3,"decision":YES}}
        :param algo_conf: An algorithm configuration (to specify which algorithm to launch)
        :param pic_package_from: first picture dict
        :param pic_package_to: second picture dict
        :param answer: Current dict of algo_name to algo match (will be updated and returned)
        :return: a dict of algo_name to algo match
        """

        algo_name = algo_conf.get('algo_name')

        # Depending on the type of
        # self.logger.debug(f"Comparison for BOW : {self.dist_conf.BOW_CMP_HIST} of {type(self.dist_conf.BOW_CMP_HIST)} "
        # and {distance_engine_conf.BOW_CMP_HIST.CORREL.name} of {type(distance_engine_conf.BOW_CMP_HIST.CORREL.name)}")

        if self.dist_conf.BOW_CMP_HIST == distance_engine_conf.BOW_CMP_HIST.CORREL.name:
            tmp_dist = 1 - cv2.compareHist(pic_package_from["BOW_ORB_DESCRIPTOR"],
                                           pic_package_to["BOW_ORB_DESCRIPTOR"],
                                           cv2.HISTCMP_CORREL)
        elif self.dist_conf.BOW_CMP_HIST == distance_engine_conf.BOW_CMP_HIST.BHATTACHARYYA.name:
            tmp_dist = cv2.compareHist(pic_package_from["BOW_ORB_DESCRIPTOR"],
                                       pic_package_to["BOW_ORB_DESCRIPTOR"],
                                       cv2.HISTCMP_BHATTACHARYYA)
        else:
            raise Exception('BOW ORB : HISTOGRAM COMPARISON MODE INCORRECT')

        # Add the distance as an AlgoMatch
        answer[algo_name] = sd.AlgoMatch(name=algo_name,
                                         distance=tmp_dist,
                                         decision=self.compute_decision_from_distance(algo_conf, tmp_dist))
        return answer

    # ==================== ------ DECISIONS ------- ====================

    @staticmethod
    def compute_decision_from_distance(algo_conf: Algo_conf, dist: float) -> sd.DecisionTypes:
        """
        From a distance between orb distance, gives a decision : is it a match or not ? Or maybe ?
        # TODO : Evolve to more complex calculation if needed for ORB !
        :param algo_conf: An algorithm configuration (to specify which algorithm to launch)
        :param dist: a distance between two pictures
        :return: a decision (YES,MAYBE,NO)
        """

        return dist_hash.compute_decision_from_distance(algo_conf, dist)
