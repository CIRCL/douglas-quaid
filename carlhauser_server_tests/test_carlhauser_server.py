# -*- coding: utf-8 -*-
import subprocess
import time
import unittest

import redis
import logging

from carlhauser_server.Helpers.environment_variable import get_homedir
import carlhauser_server.Configuration.database_conf as database_conf
import carlhauser_server.DatabaseAccessor.database_worker as database_worker
import carlhauser_server.Helpers.database_start_stop as database_start_stop
from carlhauser_server_tests.context import *


class testCarlHauserServer(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()
        # self.conf = .Default_configuration()
        # self.test_file_path = get_homedir() / pathlib.Path("carlhauser_server_tests/test_Helpers/environment_variable")

        self.db_conf = database_conf.Default_database_conf()

        # Create database handler from configuration file
        self.db_handler = database_start_stop.Database_StartStop(conf=self.db_conf)

        # Test data
        self.db_handler.test_socket_path = get_homedir() / self.db_conf.DB_SOCKETS_PATH / 'test.sock'
        self.db_handler.launch_test_script_path = get_homedir() / self.db_conf.DB_SCRIPTS_PATH / "run_redis_test.sh"
        self.db_handler.shutdown_test_script_path = get_homedir() / self.db_conf.DB_SCRIPTS_PATH / "shutdown_redis_test.sh"

        # Launch test Redis DB
        if not self.db_handler.check_running('test'):
            subprocess.Popen([str(self.db_handler.launch_test_script_path)], cwd=(self.db_handler.launch_test_script_path.parent))

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

    def test_db_worker_add_queue(self):
        # Construct a worker and get a link to redis db
        db_worker = database_worker.Database_Worker(self.db_conf)
        test_db = redis.Redis(unix_socket_path=self.db_handler.get_socket_path('test'), decode_responses=True)

        # Create data
        queue_name = "test"
        id_to_process = str(42)
        data_to_store = {"img": "MyPerfectPicture", "test": "test_value"}

        # try to store it
        db_worker.add_to_queue(test_db, queue_name, id_to_process, data_to_store)
        print("Data stored id :", id_to_process, " data : ", data_to_store)

        # Verify if the data had been stored
        id_hashset = test_db.lrange(queue_name, 0, -1)
        print("Queue_list", id_hashset)
        self.assertEqual(len(id_hashset), 1)
        tmp_dict = test_db.hgetall(id_hashset[0])
        print("Stored values", tmp_dict)
        self.assertEqual(len(tmp_dict), 2)
        self.assertEqual(tmp_dict, data_to_store)

        data_to_store = {"img": "MyPerfectPicture", "test": "test_value", "list": ["value1", "value2"]}
        # TODO : Please not that list in dict are not handled by pyredis

    def test_db_worker_get_from_queue(self):
        # Construct a worker and get a link to redis db
        db_worker = database_worker.Database_Worker(self.db_conf)
        test_db = redis.Redis(unix_socket_path=self.db_handler.get_socket_path('test'), decode_responses=True)

        # Create data
        queue_name = "test"
        id_to_process = str(42)
        data_to_store = {"img": "MyPerfectPicture", "test": "test_value"}

        # try to store it
        tmp_id_to_store = '|'.join([queue_name, id_to_process])  # create the key
        test_db.hmset(tmp_id_to_store, data_to_store)
        test_db.rpush(queue_name, tmp_id_to_store)  # Add the id to the queue
        print("Data stored, data : ", data_to_store, " in (variable) ", tmp_id_to_store)
        print("Data stored, data : ", tmp_id_to_store, " in (queue) ", queue_name)

        # Verify if the data had been stored
        tmp_id, tmp_dict = db_worker.get_from_queue(test_db, queue_name)
        print("Stored values, id : ", tmp_id)
        print("Stored values, dict : ", tmp_dict)
        self.assertEqual(len(tmp_dict), 2)
        self.assertEqual(tmp_dict, data_to_store)
        self.assertEqual(tmp_id, id_to_process)

    def test_db_worker_set_get_queue_consistency(self):
        # Construct a worker and get a link to redis db
        db_worker = database_worker.Database_Worker(self.db_conf)
        test_db = redis.Redis(unix_socket_path=self.db_handler.get_socket_path('test'), decode_responses=True)

        # Create data
        queue_name = "test"
        id_to_process = str(42)
        data_to_store = {"img": "MyPerfectPicture", "test": "test_value"}

        # try to store it
        db_worker.add_to_queue(test_db, queue_name, id_to_process, data_to_store)
        print("Data stored id :", id_to_process, " data : ", data_to_store)

        # Verify if the data had been stored
        tmp_id, tmp_dict = db_worker.get_from_queue(test_db, queue_name)
        print("Stored values, id : ", tmp_id)
        print("Stored values, dict : ", tmp_dict)
        self.assertEqual(len(tmp_dict), 2)
        self.assertEqual(tmp_dict, data_to_store)
        self.assertEqual(tmp_id, id_to_process)

    def test_absolute_truth_and_meaning(self):
        assert True


if __name__ == '__main__':
    unittest.main()
