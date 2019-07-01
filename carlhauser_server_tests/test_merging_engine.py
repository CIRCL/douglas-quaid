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


class testDistanceEngine(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()
        # self.conf = .Default_configuration()
        # self.test_file_path = get_homedir() / pathlib.Path("carlhauser_server_tests/test_Helpers/environment_variable")

        self.db_conf = database_conf.Default_database_conf()
        self.dist_conf = distance_engine_conf.Default_distance_engine_conf()
        self.fe_conf = feature_extractor_conf.Default_feature_extractor_conf()

        # Create database handler from configuration file
        self.db_handler = database_start_stop.Database_StartStop(db_conf=self.db_conf)

        # Test data
        self.db_handler.test_socket_path = get_homedir() / self.db_conf.DB_SOCKETS_PATH / 'test.sock'
        self.db_handler.launch_test_script_path = get_homedir() / self.db_conf.DB_SCRIPTS_PATH / "run.sh"
        self.db_handler.shutdown_test_script_path = get_homedir() / self.db_conf.DB_SCRIPTS_PATH / "shutdown.sh"

        # Construct a worker and get a link to redis db
        self.db_adder = database_adder.Database_Adder(self.db_conf, self.dist_conf, self.fe_conf)
        self.db_adder.storage_db_decode = redis.Redis(unix_socket_path=self.db_handler.get_socket_path('test'), decode_responses=True)
        self.db_adder.storage_db_no_decode = redis.Redis(unix_socket_path=self.db_handler.get_socket_path('test'), decode_responses=False)
        self.de = distance_engine.Distance_Engine(self.db_adder, self.db_conf, self.dist_conf, self.fe_conf)
        test_db = redis.Redis(unix_socket_path=self.db_handler.get_socket_path('test'), decode_responses=True)

        self.de.storage_db = test_db

        # Launch test Redis DB
        if not self.db_handler.is_running('test'):
            subprocess.Popen([str(self.db_handler.launch_test_script_path)], cwd=self.db_handler.launch_test_script_path.parent)

        # Time for the socket to be opened
        time.sleep(1)

        self.me = merging_engine.Merging_Engine(self.db_conf, self.dist_conf, self.fe_conf)

    def tearDown(self):
        # Shutdown test Redis DB
        if self.db_handler.is_running('test'):
            subprocess.Popen([str(self.db_handler.shutdown_test_script_path)], cwd=self.db_handler.test_socket_path.parent)

        # If start and stop are too fast, then it can't stop nor start, as it can't connect
        # e.g. because the new socket couldn't be create as the last one is still here
        time.sleep(1)

        # TODO : Kill subprocess ?


    '''
        def test_get_top_matching_clusters(self):
        id_to_process = str(42)
        data_to_store = {"P-HASH":"0000000111100","ORB":"orb_desriptors_list"}
        #TODO : Make better example

        # Add picture to storage
        list_clusters = self.ce.get_top_matching_clusters(data_to_store)

        # Checks
        self.assertEqual([0,1,2],list_clusters)
    '''


    def test_absolute_truth_and_meaning(self):
        self.assertTrue(True)

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
        self.me.fe_conf.A_HASH.decision_weight = 1
        self.me.fe_conf.P_HASH.decision_weight = 1
        self.me.fe_conf.D_HASH.decision_weight = 1
        self.me.fe_conf.ORB.decision_weight = 5

        dict_matches = {
            "A_HASH" : sd.AlgoMatch(name="A_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "P_HASH" : sd.AlgoMatch(name="P_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "D_HASH" : sd.AlgoMatch(name="D_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
        }
        answer = self.me.get_pareto_decision(dict_matches)
        self.logger.info(f"Pareto YYY {answer}")
        self.assertEqual(answer, sd.DecisionTypes.YES)

        dict_matches = {
            "A_HASH" : sd.AlgoMatch(name="A_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
            "P_HASH" : sd.AlgoMatch(name="P_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
            "D_HASH" : sd.AlgoMatch(name="D_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
        }
        answer = self.me.get_pareto_decision(dict_matches)
        self.logger.info(f"Pareto NNN {answer}")
        self.assertEqual(answer, sd.DecisionTypes.NO)

        dict_matches = {
            "A_HASH" : sd.AlgoMatch(name="A_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "P_HASH" : sd.AlgoMatch(name="P_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
            "D_HASH" : sd.AlgoMatch(name="D_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
        }
        answer = self.me.get_pareto_decision(dict_matches)
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
        self.me.fe_conf.A_HASH.decision_weight = 1
        self.me.fe_conf.P_HASH.decision_weight = 1
        self.me.fe_conf.D_HASH.decision_weight = 1
        self.me.fe_conf.ORB.decision_weight = 5

        dict_matches = {
            "A_HASH" : sd.AlgoMatch(name="A_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "P_HASH" : sd.AlgoMatch(name="P_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "D_HASH" : sd.AlgoMatch(name="D_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
        }
        answer = self.me.get_majority_decision(dict_matches)
        self.logger.info(f"Majority YYY {answer}")
        self.assertEqual(answer, sd.DecisionTypes.YES)

        dict_matches = {
            "A_HASH" : sd.AlgoMatch(name="A_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
            "P_HASH" : sd.AlgoMatch(name="P_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
            "D_HASH" : sd.AlgoMatch(name="D_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
        }
        answer = self.me.get_majority_decision(dict_matches)
        self.logger.info(f"Majority NNN {answer}")
        self.assertEqual(answer, sd.DecisionTypes.NO)

        dict_matches = {
            "A_HASH" : sd.AlgoMatch(name="A_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "P_HASH" : sd.AlgoMatch(name="P_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
            "D_HASH" : sd.AlgoMatch(name="D_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
        }
        answer = self.me.get_majority_decision(dict_matches)
        self.logger.info(f"Majority YNN {answer}")
        self.assertEqual(answer, sd.DecisionTypes.NO)

        dict_matches = {
            "A_HASH" : sd.AlgoMatch(name="A_HASH", distance=0.0, decision=sd.DecisionTypes.MAYBE),
            "P_HASH" : sd.AlgoMatch(name="P_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
            "D_HASH" : sd.AlgoMatch(name="D_HASH", distance=0.0, decision=sd.DecisionTypes.MAYBE),
        }
        answer = self.me.get_majority_decision(dict_matches)
        self.logger.info(f"Majority MNM {answer}")
        self.assertEqual(answer, sd.DecisionTypes.MAYBE)

        dict_matches = {
            "A_HASH" : sd.AlgoMatch(name="A_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
            "P_HASH" : sd.AlgoMatch(name="P_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "ORB" : sd.AlgoMatch(name="ORB", distance=0.0, decision=sd.DecisionTypes.MAYBE),
        }
        answer = self.me.get_majority_decision(dict_matches)
        self.logger.info(f"Majority NYM {answer}")
        self.assertEqual(answer, sd.DecisionTypes.YES)

        dict_matches = {
            "A_HASH" : sd.AlgoMatch(name="A_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "P_HASH" : sd.AlgoMatch(name="P_HASH", distance=0.0, decision=sd.DecisionTypes.MAYBE),
            "D_HASH" : sd.AlgoMatch(name="D_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
        }
        answer = self.me.get_majority_decision(dict_matches)
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

        self.me.fe_conf.A_HASH.decision_weight = 1
        self.me.fe_conf.P_HASH.decision_weight = 1
        self.me.fe_conf.D_HASH.decision_weight = 1
        self.me.fe_conf.ORB.decision_weight = 5

        dict_matches = {
            "A_HASH" : sd.AlgoMatch(name="A_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "P_HASH" : sd.AlgoMatch(name="P_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "D_HASH" : sd.AlgoMatch(name="D_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
        }
        answer = self.me.get_weighted_majority_decision(dict_matches)
        self.logger.info(f"Majority YYY {answer}")
        self.assertEqual(answer, sd.DecisionTypes.YES)

        dict_matches = {
            "A_HASH" : sd.AlgoMatch(name="A_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
            "P_HASH" : sd.AlgoMatch(name="P_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
            "D_HASH" : sd.AlgoMatch(name="D_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
        }
        answer = self.me.get_weighted_majority_decision(dict_matches)
        self.logger.info(f"Majority NNN {answer}")
        self.assertEqual(answer, sd.DecisionTypes.NO)

        dict_matches = {
            "A_HASH" : sd.AlgoMatch(name="A_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "P_HASH" : sd.AlgoMatch(name="P_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
            "D_HASH" : sd.AlgoMatch(name="D_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
        }
        answer = self.me.get_weighted_majority_decision(dict_matches)
        self.logger.info(f"Majority YNN {answer}")
        self.assertEqual(answer, sd.DecisionTypes.NO)

        dict_matches = {
            "A_HASH" : sd.AlgoMatch(name="A_HASH", distance=0.0, decision=sd.DecisionTypes.MAYBE),
            "P_HASH" : sd.AlgoMatch(name="P_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
            "D_HASH" : sd.AlgoMatch(name="D_HASH", distance=0.0, decision=sd.DecisionTypes.MAYBE),
        }
        answer = self.me.get_weighted_majority_decision(dict_matches)
        self.logger.info(f"Majority MNM {answer}")
        self.assertEqual(answer, sd.DecisionTypes.MAYBE)

        dict_matches = {
            "A_HASH" : sd.AlgoMatch(name="A_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
            "P_HASH" : sd.AlgoMatch(name="P_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "ORB" : sd.AlgoMatch(name="ORB", distance=0.0, decision=sd.DecisionTypes.MAYBE),
        }
        answer = self.me.get_weighted_majority_decision(dict_matches)
        self.logger.info(f"Majority NYM with ORB MAYBE {answer}")
        self.assertEqual(answer, sd.DecisionTypes.MAYBE)

        dict_matches = {
            "A_HASH" : sd.AlgoMatch(name="A_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "P_HASH" : sd.AlgoMatch(name="P_HASH", distance=0.0, decision=sd.DecisionTypes.MAYBE),
            "D_HASH" : sd.AlgoMatch(name="D_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
        }
        answer = self.me.get_weighted_majority_decision(dict_matches)
        self.logger.info(f"Majority YMN {answer}")
        # Because we want false positive instead of false negative
        self.assertEqual(answer, sd.DecisionTypes.YES)

        dict_matches = {
            "A_HASH" : sd.AlgoMatch(name="A_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "P_HASH" : sd.AlgoMatch(name="P_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "D_HASH" : sd.AlgoMatch(name="D_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "TLSH" : sd.AlgoMatch(name="TLSH", distance=0.0, decision=sd.DecisionTypes.YES),
            "ORB" : sd.AlgoMatch(name="ORB", distance=0.0, decision=sd.DecisionTypes.NO),
        }
        answer = self.me.get_weighted_majority_decision(dict_matches)
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

        self.me.fe_conf.A_HASH.decision_weight = 1
        self.me.fe_conf.P_HASH.decision_weight = 1
        self.me.fe_conf.D_HASH.decision_weight = 1
        self.me.fe_conf.ORB.decision_weight = 5

        dict_matches = {
            "A_HASH" : sd.AlgoMatch(name="A_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "P_HASH" : sd.AlgoMatch(name="P_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "D_HASH" : sd.AlgoMatch(name="D_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
        }
        answer = self.me.get_pyramid_decision(dict_matches)
        self.logger.info(f"Pyramid YYY {answer}")
        self.assertEqual(answer, sd.DecisionTypes.YES)

        dict_matches = {
            "A_HASH" : sd.AlgoMatch(name="A_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
            "P_HASH" : sd.AlgoMatch(name="P_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
            "D_HASH" : sd.AlgoMatch(name="D_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
        }
        answer = self.me.get_pyramid_decision(dict_matches)
        self.logger.info(f"Pyramid NNN {answer}")
        self.assertEqual(answer, sd.DecisionTypes.NO)

        dict_matches = {
            "A_HASH" : sd.AlgoMatch(name="A_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "P_HASH" : sd.AlgoMatch(name="P_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
            "D_HASH" : sd.AlgoMatch(name="D_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
        }
        answer = self.me.get_pyramid_decision(dict_matches)
        self.logger.info(f"Pyramid YNN {answer}")
        self.assertEqual(answer, sd.DecisionTypes.NO)

        dict_matches = {
            "A_HASH" : sd.AlgoMatch(name="A_HASH", distance=0.0, decision=sd.DecisionTypes.MAYBE),
            "P_HASH" : sd.AlgoMatch(name="P_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
            "D_HASH" : sd.AlgoMatch(name="D_HASH", distance=0.0, decision=sd.DecisionTypes.MAYBE),
        }
        answer = self.me.get_pyramid_decision(dict_matches)
        self.logger.info(f"Pyramid MNM {answer}")
        self.assertEqual(answer, sd.DecisionTypes.MAYBE)

        dict_matches = {
            "A_HASH" : sd.AlgoMatch(name="A_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
            "P_HASH" : sd.AlgoMatch(name="P_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "ORB" : sd.AlgoMatch(name="ORB", distance=0.0, decision=sd.DecisionTypes.MAYBE),
        }
        answer = self.me.get_pyramid_decision(dict_matches)
        self.logger.info(f"Pyramid NYM with ORB MAYBE {answer}")
        self.assertEqual(answer, sd.DecisionTypes.YES)

        dict_matches = {
            "A_HASH" : sd.AlgoMatch(name="A_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "P_HASH" : sd.AlgoMatch(name="P_HASH", distance=0.0, decision=sd.DecisionTypes.MAYBE),
            "D_HASH" : sd.AlgoMatch(name="D_HASH", distance=0.0, decision=sd.DecisionTypes.NO),
        }
        answer = self.me.get_pyramid_decision(dict_matches)
        self.logger.info(f"Pyramid YMN {answer}")
        # Because we want false positive instead of false negative
        self.assertEqual(answer, sd.DecisionTypes.YES)

        dict_matches = {
            "A_HASH" : sd.AlgoMatch(name="A_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "P_HASH" : sd.AlgoMatch(name="P_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "D_HASH" : sd.AlgoMatch(name="D_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "TLSH" : sd.AlgoMatch(name="TLSH", distance=0.0, decision=sd.DecisionTypes.YES),
            "ORB" : sd.AlgoMatch(name="ORB", distance=0.0, decision=sd.DecisionTypes.NO),
        }
        answer = self.me.get_pyramid_decision(dict_matches)
        self.logger.info(f"Pyramid YYYYN with ORB NO {answer}")
        self.assertEqual(answer, sd.DecisionTypes.NO)

        self.me.fe_conf.A_HASH.decision_weight = 1
        self.me.fe_conf.P_HASH.decision_weight = 1
        self.me.fe_conf.D_HASH.decision_weight = 2
        self.me.fe_conf.ORB.decision_weight = 5

        dict_matches = {
            "A_HASH" : sd.AlgoMatch(name="A_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "P_HASH" : sd.AlgoMatch(name="P_HASH", distance=0.0, decision=sd.DecisionTypes.YES),
            "D_HASH" : sd.AlgoMatch(name="D_HASH", distance=0.0, decision=sd.DecisionTypes.MAYBE),
            "TLSH" : sd.AlgoMatch(name="TLSH", distance=0.0, decision=sd.DecisionTypes.MAYBE),
            "ORB" : sd.AlgoMatch(name="ORB", distance=0.0, decision=sd.DecisionTypes.MAYBE),
        }
        answer = self.me.get_pyramid_decision(dict_matches)
        self.logger.info(f"Pyramid YYMMM with ORB MAYBE {answer}")
        self.assertEqual(answer, sd.DecisionTypes.YES)

if __name__ == '__main__':
    unittest.main()
