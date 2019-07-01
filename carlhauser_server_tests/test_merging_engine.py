# -*- coding: utf-8 -*-

import subprocess
import time
import unittest

import redis
import logging

from carlhauser_server.Helpers.environment_variable import get_homedir
import carlhauser_server.Configuration.database_conf as database_conf
import carlhauser_server.Configuration.distance_engine_conf as distance_engine_conf
import carlhauser_server.Configuration.feature_extractor_conf as feature_extractor_conf
import carlhauser_server.DistanceEngine.distance_engine as distance_engine
import carlhauser_server.Helpers.database_start_stop as database_start_stop
import carlhauser_server.DatabaseAccessor.database_adder as database_adder
import carlhauser_server.DistanceEngine.merging_engine as merging_engine
import carlhauser_server.DistanceEngine.scoring_datastrutures as sd
import common.TestDBHandler.test_instance_launcher as test_database_handler


class testDistanceEngine(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()

        # Create configurations
        self.test_db_conf = test_database_handler.TestInstance_database_conf()
        self.dist_conf = distance_engine_conf.Default_distance_engine_conf()
        self.fe_conf = feature_extractor_conf.Default_feature_extractor_conf()

        self.test_db_handler = test_database_handler.TestInstanceLauncher()
        self.db_adder = database_adder.Database_Adder(self.test_db_conf, self.dist_conf, self.fe_conf)
        self.distance_engine = distance_engine.Distance_Engine(self.db_adder, self.test_db_conf, self.dist_conf, self.fe_conf)
        self.merging_engine = merging_engine.Merging_Engine(self.test_db_conf, self.dist_conf, self.fe_conf)

    def test_absolute_truth_and_meaning(self):
        self.assertTrue(True)
        print("\nPassing\n")

    def test_get_pareto_decision(self):
        '''
        self.A_HASH = Algo_conf("A_HASH", False, 0.2, 0.6, distance_weight=1)
        self.P_HASH = Algo_conf("P_HASH", True, 0.2, 0.6, distance_weight=1)
        self.P_HASH_SIMPLE = Algo_conf("P_HASH_SIMPLE", False, 0.2, 0.6, distance_weight=1)
        self.D_HASH = Algo_conf("D_HASH", True, 0.2, 0.6, distance_weight=1)
        self.D_HASH_VERTICAL = Algo_conf("D_HASH_VERTICAL", False, 0.2, 0.6, distance_weight=1)
        self.W_HASH = Algo_conf("W_HASH", False, 0.2, 0.6, distance_weight=1)
        self.TLSH = Algo_conf("TLSH", True, 0.2, 0.6, distance_weight=1)

        # Visual Descriptors parameters
        self.ORB = Algo_conf("ORB", True, 0.2, 0.6, distance_weight=5)
        '''
        self.merging_engine.fe_conf.A_HASH.decision_weight = 1
        self.merging_engine.fe_conf.P_HASH.decision_weight = 1
        self.merging_engine.fe_conf.D_HASH.decision_weight = 1
        self.merging_engine.fe_conf.ORB.decision_weight = 5

        dict_matches = {
            "A_HASH": sd.AlgoMatch(name="A_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "P_HASH": sd.AlgoMatch(name="P_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "D_HASH": sd.AlgoMatch(name="D_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
        }
        answer = self.merging_engine.get_pareto_decision(dict_matches)
        self.logger.info(f"Pareto YYY {answer}")
        self.assertEqual(answer, sd.DecisionTypes.YES)

        dict_matches = {
            "A_HASH": sd.AlgoMatch(name="A_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
            "P_HASH": sd.AlgoMatch(name="P_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
            "D_HASH": sd.AlgoMatch(name="D_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
        }
        answer = self.merging_engine.get_pareto_decision(dict_matches)
        self.logger.info(f"Pareto NNN {answer}")
        self.assertEqual(answer, sd.DecisionTypes.NO)

        dict_matches = {
            "A_HASH": sd.AlgoMatch(name="A_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "P_HASH": sd.AlgoMatch(name="P_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
            "D_HASH": sd.AlgoMatch(name="D_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
        }
        answer = self.merging_engine.get_pareto_decision(dict_matches)
        self.logger.info(f"Pareto YNN {answer}")
        self.assertEqual(answer, sd.DecisionTypes.MAYBE)

    def test_get_majority_decision(self):
        '''
        self.A_HASH = Algo_conf("A_HASH", False, 0.2, 0.6, distance_weight=1)
        self.P_HASH = Algo_conf("P_HASH", True, 0.2, 0.6, distance_weight=1)
        self.P_HASH_SIMPLE = Algo_conf("P_HASH_SIMPLE", False, 0.2, 0.6, distance_weight=1)
        self.D_HASH = Algo_conf("D_HASH", True, 0.2, 0.6, distance_weight=1)
        self.D_HASH_VERTICAL = Algo_conf("D_HASH_VERTICAL", False, 0.2, 0.6, distance_weight=1)
        self.W_HASH = Algo_conf("W_HASH", False, 0.2, 0.6, distance_weight=1)
        self.TLSH = Algo_conf("TLSH", True, 0.2, 0.6, distance_weight=1)

        # Visual Descriptors parameters
        self.ORB = Algo_conf("ORB", True, 0.2, 0.6, distance_weight=5)
        '''
        self.merging_engine.fe_conf.A_HASH.decision_weight = 1
        self.merging_engine.fe_conf.P_HASH.decision_weight = 1
        self.merging_engine.fe_conf.D_HASH.decision_weight = 1
        self.merging_engine.fe_conf.ORB.decision_weight = 5

        dict_matches = {
            "A_HASH": sd.AlgoMatch(name="A_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "P_HASH": sd.AlgoMatch(name="P_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "D_HASH": sd.AlgoMatch(name="D_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
        }
        answer = self.merging_engine.get_majority_decision(dict_matches)
        self.logger.info(f"Majority YYY {answer}")
        self.assertEqual(answer, sd.DecisionTypes.YES)

        dict_matches = {
            "A_HASH": sd.AlgoMatch(name="A_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
            "P_HASH": sd.AlgoMatch(name="P_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
            "D_HASH": sd.AlgoMatch(name="D_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
        }
        answer = self.merging_engine.get_majority_decision(dict_matches)
        self.logger.info(f"Majority NNN {answer}")
        self.assertEqual(answer, sd.DecisionTypes.NO)

        dict_matches = {
            "A_HASH": sd.AlgoMatch(name="A_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "P_HASH": sd.AlgoMatch(name="P_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
            "D_HASH": sd.AlgoMatch(name="D_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
        }
        answer = self.merging_engine.get_majority_decision(dict_matches)
        self.logger.info(f"Majority YNN {answer}")
        self.assertEqual(answer, sd.DecisionTypes.NO)

        dict_matches = {
            "A_HASH": sd.AlgoMatch(name="A_HASH", distance=0.0, decision=sd.DecisionTypes.MAYBE),
            "P_HASH": sd.AlgoMatch(name="P_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
            "D_HASH": sd.AlgoMatch(name="D_HASH", distance=0.0, decision=sd.DecisionTypes.MAYBE),
        }
        answer = self.merging_engine.get_majority_decision(dict_matches)
        self.logger.info(f"Majority MNM {answer}")
        self.assertEqual(answer, sd.DecisionTypes.MAYBE)

        dict_matches = {
            "A_HASH": sd.AlgoMatch(name="A_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
            "P_HASH": sd.AlgoMatch(name="P_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "ORB": sd.AlgoMatch(name="ORB", distance=0.0, decision=sd.DecisionTypes.MAYBE),
        }
        answer = self.merging_engine.get_majority_decision(dict_matches)
        self.logger.info(f"Majority NYM {answer}")
        self.assertEqual(answer, sd.DecisionTypes.YES)

        dict_matches = {
            "A_HASH": sd.AlgoMatch(name="A_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "P_HASH": sd.AlgoMatch(name="P_HASH", distance=0.0, decision=sd.DecisionTypes.MAYBE),
            "D_HASH": sd.AlgoMatch(name="D_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
        }
        answer = self.merging_engine.get_majority_decision(dict_matches)
        self.logger.info(f"Majority YMN {answer}")
        # Because we want false positive instead of false negative
        self.assertEqual(answer, sd.DecisionTypes.YES)

    def test_get_weighted_majority_decision(self):
        '''
        self.A_HASH = Algo_conf("A_HASH", False, 0.2, 0.6, distance_weight=1)
        self.P_HASH = Algo_conf("P_HASH", True, 0.2, 0.6, distance_weight=1)
        self.P_HASH_SIMPLE = Algo_conf("P_HASH_SIMPLE", False, 0.2, 0.6, distance_weight=1)
        self.D_HASH = Algo_conf("D_HASH", True, 0.2, 0.6, distance_weight=1)
        self.D_HASH_VERTICAL = Algo_conf("D_HASH_VERTICAL", False, 0.2, 0.6, distance_weight=1)
        self.W_HASH = Algo_conf("W_HASH", False, 0.2, 0.6, distance_weight=1)
        self.TLSH = Algo_conf("TLSH", True, 0.2, 0.6, distance_weight=1)

        # Visual Descriptors parameters
        self.ORB = Algo_conf("ORB", True, 0.2, 0.6, distance_weight=5)
        '''

        self.merging_engine.fe_conf.A_HASH.decision_weight = 1
        self.merging_engine.fe_conf.P_HASH.decision_weight = 1
        self.merging_engine.fe_conf.D_HASH.decision_weight = 1
        self.merging_engine.fe_conf.ORB.decision_weight = 5

        dict_matches = {
            "A_HASH": sd.AlgoMatch(name="A_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "P_HASH": sd.AlgoMatch(name="P_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "D_HASH": sd.AlgoMatch(name="D_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
        }
        answer = self.merging_engine.get_weighted_majority_decision(dict_matches)
        self.logger.info(f"Majority YYY {answer}")
        self.assertEqual(answer, sd.DecisionTypes.YES)

        dict_matches = {
            "A_HASH": sd.AlgoMatch(name="A_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
            "P_HASH": sd.AlgoMatch(name="P_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
            "D_HASH": sd.AlgoMatch(name="D_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
        }
        answer = self.merging_engine.get_weighted_majority_decision(dict_matches)
        self.logger.info(f"Majority NNN {answer}")
        self.assertEqual(answer, sd.DecisionTypes.NO)

        dict_matches = {
            "A_HASH": sd.AlgoMatch(name="A_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "P_HASH": sd.AlgoMatch(name="P_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
            "D_HASH": sd.AlgoMatch(name="D_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
        }
        answer = self.merging_engine.get_weighted_majority_decision(dict_matches)
        self.logger.info(f"Majority YNN {answer}")
        self.assertEqual(answer, sd.DecisionTypes.NO)

        dict_matches = {
            "A_HASH": sd.AlgoMatch(name="A_HASH", distance=0.0, decision=sd.DecisionTypes.MAYBE),
            "P_HASH": sd.AlgoMatch(name="P_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
            "D_HASH": sd.AlgoMatch(name="D_HASH", distance=0.0, decision=sd.DecisionTypes.MAYBE),
        }
        answer = self.merging_engine.get_weighted_majority_decision(dict_matches)
        self.logger.info(f"Majority MNM {answer}")
        self.assertEqual(answer, sd.DecisionTypes.MAYBE)

        dict_matches = {
            "A_HASH": sd.AlgoMatch(name="A_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
            "P_HASH": sd.AlgoMatch(name="P_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "ORB": sd.AlgoMatch(name="ORB", distance=0.0, decision=sd.DecisionTypes.MAYBE),
        }
        answer = self.merging_engine.get_weighted_majority_decision(dict_matches)
        self.logger.info(f"Majority NYM with ORB MAYBE {answer}")
        self.assertEqual(answer, sd.DecisionTypes.MAYBE)

        dict_matches = {
            "A_HASH": sd.AlgoMatch(name="A_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "P_HASH": sd.AlgoMatch(name="P_HASH", distance=0.0, decision=sd.DecisionTypes.MAYBE),
            "D_HASH": sd.AlgoMatch(name="D_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
        }
        answer = self.merging_engine.get_weighted_majority_decision(dict_matches)
        self.logger.info(f"Majority YMN {answer}")
        # Because we want false positive instead of false negative
        self.assertEqual(answer, sd.DecisionTypes.YES)

        dict_matches = {
            "A_HASH": sd.AlgoMatch(name="A_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "P_HASH": sd.AlgoMatch(name="P_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "D_HASH": sd.AlgoMatch(name="D_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "TLSH": sd.AlgoMatch(name="TLSH", distance=0.0, decision=sd.DecisionTypes.YES),
            "ORB": sd.AlgoMatch(name="ORB", distance=0.0, decision=sd.DecisionTypes.NO),
        }
        answer = self.merging_engine.get_weighted_majority_decision(dict_matches)
        self.logger.info(f"Majority YYYYN with ORB NO {answer}")
        self.assertEqual(answer, sd.DecisionTypes.NO)

    def test_get_pyramid_decision(self):
        '''
        self.A_HASH = Algo_conf("A_HASH", False, 0.2, 0.6, distance_weight=1)
        self.P_HASH = Algo_conf("P_HASH", True, 0.2, 0.6, distance_weight=1)
        self.P_HASH_SIMPLE = Algo_conf("P_HASH_SIMPLE", False, 0.2, 0.6, distance_weight=1)
        self.D_HASH = Algo_conf("D_HASH", True, 0.2, 0.6, distance_weight=1)
        self.D_HASH_VERTICAL = Algo_conf("D_HASH_VERTICAL", False, 0.2, 0.6, distance_weight=1)
        self.W_HASH = Algo_conf("W_HASH", False, 0.2, 0.6, distance_weight=1)
        self.TLSH = Algo_conf("TLSH", True, 0.2, 0.6, distance_weight=1)

        # Visual Descriptors parameters
        self.ORB = Algo_conf("ORB", True, 0.2, 0.6, distance_weight=5)
        '''

        self.merging_engine.fe_conf.A_HASH.decision_weight = 1
        self.merging_engine.fe_conf.P_HASH.decision_weight = 1
        self.merging_engine.fe_conf.D_HASH.decision_weight = 1
        self.merging_engine.fe_conf.ORB.decision_weight = 5

        dict_matches = {
            "A_HASH": sd.AlgoMatch(name="A_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "P_HASH": sd.AlgoMatch(name="P_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "D_HASH": sd.AlgoMatch(name="D_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
        }
        answer = self.merging_engine.get_pyramid_decision(dict_matches)
        self.logger.info(f"Pyramid YYY {answer}")
        self.assertEqual(answer, sd.DecisionTypes.YES)

        dict_matches = {
            "A_HASH": sd.AlgoMatch(name="A_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
            "P_HASH": sd.AlgoMatch(name="P_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
            "D_HASH": sd.AlgoMatch(name="D_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
        }
        answer = self.merging_engine.get_pyramid_decision(dict_matches)
        self.logger.info(f"Pyramid NNN {answer}")
        self.assertEqual(answer, sd.DecisionTypes.NO)

        dict_matches = {
            "A_HASH": sd.AlgoMatch(name="A_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "P_HASH": sd.AlgoMatch(name="P_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
            "D_HASH": sd.AlgoMatch(name="D_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
        }
        answer = self.merging_engine.get_pyramid_decision(dict_matches)
        self.logger.info(f"Pyramid YNN {answer}")
        self.assertEqual(answer, sd.DecisionTypes.NO)

        dict_matches = {
            "A_HASH": sd.AlgoMatch(name="A_HASH", distance=0.0, decision=sd.DecisionTypes.MAYBE),
            "P_HASH": sd.AlgoMatch(name="P_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
            "D_HASH": sd.AlgoMatch(name="D_HASH", distance=0.0, decision=sd.DecisionTypes.MAYBE),
        }
        answer = self.merging_engine.get_pyramid_decision(dict_matches)
        self.logger.info(f"Pyramid MNM {answer}")
        self.assertEqual(answer, sd.DecisionTypes.MAYBE)

        dict_matches = {
            "A_HASH": sd.AlgoMatch(name="A_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
            "P_HASH": sd.AlgoMatch(name="P_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "ORB": sd.AlgoMatch(name="ORB", distance=0.0, decision=sd.DecisionTypes.MAYBE),
        }
        answer = self.merging_engine.get_pyramid_decision(dict_matches)
        self.logger.info(f"Pyramid NYM with ORB MAYBE {answer}")
        self.assertEqual(answer, sd.DecisionTypes.YES)

        dict_matches = {
            "A_HASH": sd.AlgoMatch(name="A_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "P_HASH": sd.AlgoMatch(name="P_HASH", distance=0.0, decision=sd.DecisionTypes.MAYBE),
            "D_HASH": sd.AlgoMatch(name="D_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
        }
        answer = self.merging_engine.get_pyramid_decision(dict_matches)
        self.logger.info(f"Pyramid YMN {answer}")
        # Because we want false positive instead of false negative
        self.assertEqual(answer, sd.DecisionTypes.YES)

        dict_matches = {
            "A_HASH": sd.AlgoMatch(name="A_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "P_HASH": sd.AlgoMatch(name="P_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "D_HASH": sd.AlgoMatch(name="D_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "TLSH": sd.AlgoMatch(name="TLSH", distance=0.0, decision=sd.DecisionTypes.YES),
            "ORB": sd.AlgoMatch(name="ORB", distance=0.0, decision=sd.DecisionTypes.NO),
        }
        answer = self.merging_engine.get_pyramid_decision(dict_matches)
        self.logger.info(f"Pyramid YYYYN with ORB NO {answer}")
        self.assertEqual(answer, sd.DecisionTypes.NO)

        self.merging_engine.fe_conf.A_HASH.decision_weight = 1
        self.merging_engine.fe_conf.P_HASH.decision_weight = 1
        self.merging_engine.fe_conf.D_HASH.decision_weight = 2
        self.merging_engine.fe_conf.ORB.decision_weight = 5

        dict_matches = {
            "A_HASH": sd.AlgoMatch(name="A_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "P_HASH": sd.AlgoMatch(name="P_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "D_HASH": sd.AlgoMatch(name="D_HASH", distance=0.0, decision=sd.DecisionTypes.MAYBE),
            "TLSH": sd.AlgoMatch(name="TLSH", distance=0.0, decision=sd.DecisionTypes.MAYBE),
            "ORB": sd.AlgoMatch(name="ORB", distance=0.0, decision=sd.DecisionTypes.MAYBE),
        }
        answer = self.merging_engine.get_pyramid_decision(dict_matches)
        self.logger.info(f"Pyramid YYMMM with ORB MAYBE {answer}")
        self.assertEqual(answer, sd.DecisionTypes.YES)


if __name__ == '__main__':
    unittest.main()
