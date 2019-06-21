#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
# ==================== ------ STD LIBRARIES ------- ====================
import sys
import tlsh
from typing import Dict
import traceback

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))

import carlhauser_server.Configuration.database_conf as database_conf
import carlhauser_server.Configuration.distance_engine_conf as distance_engine_conf
import carlhauser_server.Configuration.feature_extractor_conf as feature_extractor_conf
import carlhauser_server.DistanceEngine.scoring_datastrutures as sd


class Distance_Hash:
    def __init__(self, db_conf: database_conf, dist_conf: distance_engine_conf, fe_conf: feature_extractor_conf):
        # STD attributes
        self.logger = logging.getLogger(__name__)
        self.logger.info("Creation of a Distance Hash Engine")

        # Save configuration
        self.db_conf = db_conf  # TODO : REMOVE = NOT USEFUL FOR NOW !
        self.dist_conf = dist_conf
        self.fe_conf = fe_conf

    # ==================== ------ INTER ALGO DISTANCE ------- ====================

    def hash_distance(self, pic_package_from, pic_package_to)-> Dict[str, sd.AlgoMatch]:
        answer = {}
        self.logger.info("Hash distance computation ... ")

        try:
            if self.fe_conf.A_HASH.get("is_enabled", False):
                answer = self.add_results(self.fe_conf.A_HASH, pic_package_from, pic_package_to, answer)
                '''
                self.logger.debug("A-HASH ... ")
                tmp_dist = self.compute_hash_distance(pic_package_from["A_HASH"], pic_package_to["A_HASH"])
                answer["A_HASH"] = sd.AlgoMatch(name="A_HASH",
                                                distance=tmp_dist,
                                                decision=)
                '''

            if self.fe_conf.P_HASH.get("is_enabled", False):
                answer = self.add_results(self.fe_conf.P_HASH, pic_package_from, pic_package_to, answer)
                '''
                self.logger.debug("P_HASH ... ")
                answer["P_HASH"] = self.compute_hash_distance(pic_package_from["P_HASH"], pic_package_to["P_HASH"])
                '''

            if self.fe_conf.P_HASH_SIMPLE.get("is_enabled", False):
                answer = self.add_results(self.fe_conf.P_HASH_SIMPLE, pic_package_from, pic_package_to, answer)

                '''
                self.logger.debug("P_HASH_SIMPLE ... ")
                answer["P_HASH_SIMPLE"] = self.compute_hash_distance(pic_package_from["P_HASH_SIMPLE"], pic_package_to["P_HASH_SIMPLE"])
                '''

            if self.fe_conf.D_HASH.get("is_enabled", False):
                answer = self.add_results(self.fe_conf.D_HASH, pic_package_from, pic_package_to, answer)

                '''
                self.logger.debug("D_HASH ... ")
                answer["D_HASH"] = self.compute_hash_distance(pic_package_from["D_HASH"], pic_package_to["D_HASH"])
                '''

            if self.fe_conf.D_HASH_VERTICAL.get("is_enabled", False):
                answer = self.add_results(self.fe_conf.D_HASH_VERTICAL, pic_package_from, pic_package_to, answer)

                '''
                self.logger.debug("D_HASH_VERTICAL ... ")
                answer["D_HASH_VERTICAL"] = self.compute_hash_distance(pic_package_from["D_HASH_VERTICAL"], pic_package_to["D_HASH_VERTICAL"])
                '''

            if self.fe_conf.W_HASH.get("is_enabled", False):
                answer = self.add_results(self.fe_conf.W_HASH, pic_package_from, pic_package_to, answer)

                '''
                self.logger.debug("W_HASH ... ")
                answer["W_HASH"] = self.compute_hash_distance(pic_package_from["W_HASH"], pic_package_to["W_HASH"])      
                '''

            if self.fe_conf.TLSH.get("is_enabled", False):
                answer = self.add_results(self.fe_conf.TLSH, pic_package_from, pic_package_to, answer)

                '''
                self.logger.debug("TLSH ... ")
                answer["TLSH"] = self.compute_tlsh_distance(pic_package_from["TLSH"], pic_package_to["TLSH"])
                '''

        except Exception as e:
            self.logger.error(traceback.print_tb(e.__traceback__))
            self.logger.error("Error during distance computation : " + str(e))

        return answer

    def add_results(self, algo_conf: feature_extractor_conf.Algo_conf, pic_package_from, pic_package_to, answer: Dict) -> Dict:
        # Add results to answer dict, depending on the algorithm name we want to compute
        # Ex : Input {} -> Output {"P-HASH":{"name":"P-HASH", "distance":0.3,"decision":YES}}
        algo_name = algo_conf.get('algo_name')

        if algo_name != "TLSH":
            # We want to compute any hash, except tlsh
            tmp_dist = self.compute_hash_distance(pic_package_from[algo_name],
                                                  pic_package_to[algo_name])
        else:
            # We want to compute tlsh distance
            tmp_dist = self.compute_tlsh_distance(pic_package_from[algo_name],
                                                  pic_package_to[algo_name])

        # Add the distance as an AlgoMatch
        answer[algo_name] = sd.AlgoMatch(name=algo_name,
                                         distance=tmp_dist,
                                         decision=self.compute_decision_from_distance(algo_conf, tmp_dist))
        return answer

    # ==================== ------ CORE COMPUTATION FOR HASHES ------- ====================

    @staticmethod
    def compute_hash_distance(hash1, hash2) -> float:
        # TODO : Check if the size is accessible. Probably not.
        return abs(hash1 - hash2) / (hash1.hash.size * 4)

    @staticmethod
    def compute_tlsh_distance(hash1, hash2) -> float:
        return tlsh.diff(hash1, hash2) / (len(hash1) * 16)  # 70 hexa character

    # ==================== ------ DECISIONS ------- ====================

    def compute_decision_from_distance(self, algo_conf: feature_extractor_conf.Algo_conf, dist: float) -> sd.DecisionTypes:
        # From a distance between hashes, gives a decision : is it a match or not ? Or maybe ?

        if dist <= algo_conf.get('threshold_maybe'):
            # It's a YES ! :)
            return sd.DecisionTypes.YES
        elif dist <= algo_conf.get('threshold_no'):
            # It's a MAYBE :/
            return sd.DecisionTypes.MAYBE
        else:
            # It's a NO :(
            return sd.DecisionTypes.NO
