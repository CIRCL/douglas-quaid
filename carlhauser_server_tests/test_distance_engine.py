# -*- coding: utf-8 -*-

import subprocess
import time
import unittest

import redis
import logging

from carlhauser_server.Helpers.environment_variable import get_homedir
import carlhauser_server.Configuration.database_conf as database_conf
import carlhauser_server.Configuration.distance_engine_conf as distance_engine_conf
import carlhauser_server.DistanceEngine.cluster_engine as cluster_engine
import carlhauser_server.Helpers.database_start_stop as database_start_stop


class testDistanceEngine(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()
        # self.conf = .Default_configuration()
        # self.test_file_path = get_homedir() / pathlib.Path("carlhauser_server_tests/test_Helpers/environment_variable")

        self.db_conf = database_conf.Default_database_conf()
        self.dist_conf = distance_engine_conf.Default_distance_engine_conf()

        # Create database handler from configuration file
        self.db_handler = database_start_stop.Database_StartStop(conf=self.db_conf)

        # Test data
        self.db_handler.test_socket_path = get_homedir() / self.db_conf.DB_SOCKETS_PATH / 'test.sock'
        self.db_handler.launch_test_script_path = get_homedir() / self.db_conf.DB_SCRIPTS_PATH / "run_redis_test.sh"
        self.db_handler.shutdown_test_script_path = get_homedir() / self.db_conf.DB_SCRIPTS_PATH / "shutdown_redis_test.sh"

        # Construct a worker and get a link to redis db
        self.ce = cluster_engine.Cluster_Engine(self.db_conf, self.dist_conf)
        test_db = redis.Redis(unix_socket_path=self.db_handler.get_socket_path('test'), decode_responses=True)
        self.ce.storage_db = test_db

        # Launch test Redis DB
        if not self.db_handler.check_running('test'):
            subprocess.Popen([str(self.db_handler.launch_test_script_path)], cwd=self.db_handler.launch_test_script_path.parent)

        # Time for the socket to be opened
        time.sleep(1)

    def tearDown(self):
        # Shutdown test Redis DB
        if self.db_handler.check_running('test'):
            subprocess.Popen([str(self.db_handler.shutdown_test_script_path)], cwd=self.db_handler.test_socket_path.parent)

        # If start and stop are too fast, then it can't stop nor start, as it can't connect
        # e.g. because the new socket couldn't be create as the last one is still here
        time.sleep(1)

        # TODO : Kill subprocess ?

    def test_add_picture_to_storage(self):
        id_to_process = str(42)
        data_to_store = {"img": "MyPerfectPicture", "test": "test_value"}
        print("Stored :", data_to_store)

        # Add picture to storage
        self.ce.add_picture_to_storage(id_to_process, data_to_store)

        # Get back data
        stored = self.ce.storage_db.hgetall(id_to_process)
        print("Fetched :", stored)

        # Checks
        self.assertEqual(data_to_store, stored)

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

    '''
        # Get top matching clusters
        list_clusters = self.ce.get_top_matching_clusters(fetched_dict)
        
        # Get top matching pictures in these clusters
        top_matching_pictures = self.ce.get_top_matching_pictures_from_clusters(list_clusters, fetched_dict)
        
        # Depending on the quality of the match ...
                    if self.ce.match_enough(top_matching_pictures[0][0]):
                        # Add picture to best picture's cluster
                        # TODO : NOPE = TOO COMPLEX FOR REVERSE LOOKUP. JUST STORED IN PREVIOUS RESULT cluster_id = self.ce.get_cluster(top_matching_pictures[0])
                        cluster_id = top_matching_pictures[0][1]
                        self.ce.add_picture_to_cluster(fetched_id, cluster_id)
                        # TODO : To defer ?
                        # Re-evaluate representative picture(s) of cluster
                        self.ce.reevaluate_representative_picture_order(fetched_id, cluster_id)
                    else:
                        # Add picture to it's own cluster
                        cluster_id = self.ce.add_picture_to_new_cluster(fetched_id)
        
                    # Add to a queue, to be reviewed later, when more pictures will be added
                    self.ce.add_to_review(fetched_id)
    '''

    def test_absolute_truth_and_meaning(self):
        assert True


if __name__ == '__main__':
    unittest.main()
