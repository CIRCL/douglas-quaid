#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import logging
import tlsh
import traceback
from typing import Dict

import carlhauser_server.Configuration.database_conf as database_conf
import carlhauser_server.Configuration.distance_engine_conf as distance_engine_conf
import carlhauser_server.Configuration.feature_extractor_conf as feature_extractor_conf
import carlhauser_server.DistanceEngine.scoring_datastrutures as sd
from carlhauser_server.Configuration.algo_conf import Algo_conf
from common.environment_variable import load_server_logging_conf_file

load_server_logging_conf_file()


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

    def hash_distance(self, pic_package_from: Dict, pic_package_to: Dict) -> Dict[str, sd.AlgoMatch]:
        """
        Distance between two provided pictures (dicts) with fuzzy hashing methods
        :param pic_package_from: first picture dict
        :param pic_package_to: second picture dict
        :return: A dictionary of algo name to the match detail (distance, decision ..)
        """
        answer = {}
        self.logger.info("Hash distance computation ... ")
        self.logger.debug("Hash distance computation ... ")

        try:
            if self.fe_conf.A_HASH.get("is_enabled", False):
                answer = self.add_results(self.fe_conf.A_HASH, pic_package_from, pic_package_to, answer)

            if self.fe_conf.P_HASH.get("is_enabled", False):
                answer = self.add_results(self.fe_conf.P_HASH, pic_package_from, pic_package_to, answer)

            if self.fe_conf.P_HASH_SIMPLE.get("is_enabled", False):
                answer = self.add_results(self.fe_conf.P_HASH_SIMPLE, pic_package_from, pic_package_to, answer)

            if self.fe_conf.D_HASH.get("is_enabled", False):
                answer = self.add_results(self.fe_conf.D_HASH, pic_package_from, pic_package_to, answer)

            if self.fe_conf.D_HASH_VERTICAL.get("is_enabled", False):
                answer = self.add_results(self.fe_conf.D_HASH_VERTICAL, pic_package_from, pic_package_to, answer)

            if self.fe_conf.W_HASH.get("is_enabled", False):
                answer = self.add_results(self.fe_conf.W_HASH, pic_package_from, pic_package_to, answer)

            if self.fe_conf.TLSH.get("is_enabled", False):
                answer = self.add_results(self.fe_conf.TLSH, pic_package_from, pic_package_to, answer)

        except Exception as e:
            self.logger.error(traceback.print_tb(e.__traceback__))
            self.logger.error(f"Error during distance computation : {e}")

        return answer

    def add_results(self, algo_conf: Algo_conf, pic_package_from: Dict, pic_package_to: Dict, answer: Dict) -> Dict[str, sd.AlgoMatch]:
        """
        Add results to answer dict, depending on the algorithm name we want to compute
        Ex : Input {} -> Output {"P-HASH":{"name":"P-HASH", "distance":0.3,"decision":YES}}
        :param algo_conf: An algorithm configuration (to specify which algorithm to launch)
        :param pic_package_from: first picture dict
        :param pic_package_to: second picture dict
        :param answer: Current dict of algo_name to algo match (will be updated and returned)
        :return: a dict of algo_name to algo match
        """

        algo_name = algo_conf.get('algo_name', None)
        self.logger.debug(f"Algo name detected : {algo_name}")

        if pic_package_from.get(algo_name, None) is None or pic_package_to.get(algo_name, None) is None:
            self.logger.warning(f"Algo hashes values are NOT presents in the results.")
            input()
        else:
            self.logger.debug(f"Algo hashes values are presents in the results.")

            if algo_name != "TLSH":
                # We want to compute any hash, except tlsh
                tmp_dist = self.compute_hash_distance(pic_package_from.get(algo_name),
                                                      pic_package_to.get(algo_name))
            else:
                # We want to compute tlsh distance
                tmp_dist = self.compute_tlsh_distance(pic_package_from.get(algo_name),
                                                      pic_package_to.get(algo_name))

            # Add the distance as an AlgoMatch
            answer[algo_name] = sd.AlgoMatch(name=algo_name,
                                             distance=tmp_dist,
                                             decision=self.compute_decision_from_distance(algo_conf, tmp_dist))
        return answer

    # ==================== ------ CORE COMPUTATION FOR HASHES ------- ====================

    @staticmethod
    def compute_hash_distance(hash1, hash2) -> float:
        """
        Compute hash difference for A-HASH, P-HASH, etc.
        :param hash1: first hash
        :param hash2: second hash
        :return: distance between hashes
        """
        # TODO : Check if the size is accessible. Probably not.
        return abs(hash1 - hash2) / (hash1.hash.size * 4)

    @staticmethod
    def compute_tlsh_distance(hash1, hash2) -> float:
        """
        Compute hash difference for TLSH only
        :param hash1: first hash
        :param hash2: second hash
        :return: distance between hashes
        """
        return tlsh.diff(hash1, hash2) / (len(hash1) * 16)  # 70 hexa character

    # ==================== ------ DECISIONS ------- ====================

    @staticmethod
    def compute_decision_from_distance(algo_conf: Algo_conf, dist: float) -> sd.DecisionTypes:
        """
        From a distance between hashes, gives a decision : is it a match or not ? Or maybe ?
        :param algo_conf: An algorithm configuration (to specify which algorithm to launch)
        :param dist: distance between hashes
        :return: A decision : YES, MAYBE or NO
        """

        if dist <= algo_conf.get('threshold_yes_to_maybe'):
            # It's a YES ! :)
            return sd.DecisionTypes.YES
        elif dist <= algo_conf.get('threshold_maybe_to_no'):
            # It's a MAYBE :/
            return sd.DecisionTypes.MAYBE
        else:
            # It's a NO :(
            return sd.DecisionTypes.NO
