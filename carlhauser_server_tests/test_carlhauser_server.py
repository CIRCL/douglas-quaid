# -*- coding: utf-8 -*-
import logging
import unittest

import redis

import carlhauser_server.DatabaseAccessor.database_worker as database_worker
import common.TestInstanceLauncher.one_db_conf as test_database_only_conf
import common.TestInstanceLauncher.one_db_instance_launcher as test_database_handler


class testCarlHauserServer(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()

        # Create configurations
        self.test_db_conf = test_database_only_conf.TestInstance_database_conf()

        self.test_db_handler = test_database_handler.TestInstanceLauncher()
        self.test_db_handler.create_full_instance(db_conf=self.test_db_conf)

        # Create database handler from test instance
        self.db_handler = self.test_db_handler.db_handler

    def tearDown(self):
        # Launch shutdown AND FLUSH script
        self.test_db_handler.tearDown()

    def test_db_worker_add_queue(self):
        # Construct a worker and get a link to redis db
        db_worker = database_worker.Database_Worker(self.test_db_conf)
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
        db_worker = database_worker.Database_Worker(self.test_db_conf)
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
        db_worker = database_worker.Database_Worker(self.test_db_conf)
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

    def test_db_worker_add_queue_no_decode(self):
        # Construct a worker and get a link to redis db
        db_worker = database_worker.Database_Worker(self.test_db_conf)
        test_db = redis.Redis(unix_socket_path=self.db_handler.get_socket_path('test'), decode_responses=False)

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

        # Manual decode
        tmp_dict = {key.decode(): val.decode() for key, val in tmp_dict.items()}

        print("Stored values", tmp_dict)
        self.assertEqual(len(tmp_dict), 2)
        self.assertEqual(tmp_dict, data_to_store)

        data_to_store = {"img": "MyPerfectPicture", "test": "test_value", "list": ["value1", "value2"]}
        # TODO : Please not that list in dict are not handled by pyredis

    def test_db_worker_get_from_queue_no_decode(self):
        # Construct a worker and get a link to redis db
        db_worker = database_worker.Database_Worker(self.test_db_conf)
        test_db = redis.Redis(unix_socket_path=self.db_handler.get_socket_path('test'), decode_responses=False)

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

        # Manual decode
        tmp_dict = {key.decode(): val.decode() for key, val in tmp_dict.items()}

        self.assertEqual(tmp_dict, data_to_store)
        self.assertEqual(tmp_id, id_to_process)

    def test_db_worker_set_get_queue_consistency_no_decode(self):
        # Construct a worker and get a link to redis db
        db_worker = database_worker.Database_Worker(self.test_db_conf)
        test_db = redis.Redis(unix_socket_path=self.db_handler.get_socket_path('test'), decode_responses=False)

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

        # Manual decode
        tmp_dict = {key.decode(): val.decode() for key, val in tmp_dict.items()}

        self.assertEqual(len(tmp_dict), 2)
        self.assertEqual(tmp_dict, data_to_store)
        self.assertEqual(tmp_id, id_to_process)

    def test_absolute_truth_and_meaning(self):
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
