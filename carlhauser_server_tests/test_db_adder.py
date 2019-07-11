#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import logging
import pathlib
import unittest

import cv2
import redis

import carlhauser_server.Configuration.distance_engine_conf as distance_engine_conf
import carlhauser_server.Configuration.feature_extractor_conf as feature_extractor_conf
import carlhauser_server.DatabaseAccessor.database_adder as database_adder
import carlhauser_server.DistanceEngine.distance_engine as distance_engine
import carlhauser_server.FeatureExtractor.picture_hasher as picture_hasher
import carlhauser_server.FeatureExtractor.picture_orber as picture_orber
import common.TestInstanceLauncher.test_instance_launcher as test_database_handler
from common.environment_variable import get_homedir
import common.TestInstanceLauncher.test_database_conf as test_database_only_conf
from carlhauser_server.Configuration.algo_conf import Algo_conf
import time
from carlhauser_server.Configuration.static_values import QueueNames


class testDBAdder(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):

        self.logger = logging.getLogger()
        self.test_file_path = get_homedir() / pathlib.Path("carlhauser_server_tests/test_DistanceEngine/")

        # Create configurations
        self.test_db_conf = test_database_only_conf.TestInstance_database_conf()
        self.dist_conf = distance_engine_conf.Default_distance_engine_conf()
        self.fe_conf = feature_extractor_conf.Default_feature_extractor_conf()

        self.fe_conf.A_HASH = Algo_conf("A_HASH", False, 0.2, 0.6, distance_weight=1)
        self.fe_conf.P_HASH = Algo_conf("P_HASH", True, 0.2, 0.6, distance_weight=1)
        self.fe_conf.P_HASH_SIMPLE = Algo_conf("P_HASH_SIMPLE", False, 0.2, 0.6, distance_weight=1)
        self.fe_conf.D_HASH = Algo_conf("D_HASH", True, 0.2, 0.6, distance_weight=1)
        self.fe_conf.D_HASH_VERTICAL = Algo_conf("D_HASH_VERTICAL", False, 0.2, 0.6, distance_weight=1)
        self.fe_conf.W_HASH = Algo_conf("W_HASH", False, 0.2, 0.6, distance_weight=1)
        self.fe_conf.TLSH = Algo_conf("TLSH", True, 0.2, 0.6, distance_weight=1)
        self.fe_conf.ORB = Algo_conf("ORB", True, 0.2, 0.6, distance_weight=1)
        self.fe_conf.list_algos = [self.fe_conf.A_HASH, self.fe_conf.P_HASH, self.fe_conf.P_HASH_SIMPLE,
                                   self.fe_conf.D_HASH, self.fe_conf.D_HASH_VERTICAL, self.fe_conf.W_HASH,
                                   self.fe_conf.TLSH,
                                   self.fe_conf.ORB]
        self.logger.debug(f"Configuration : {self.fe_conf.ORB}")

        self.test_db_handler = test_database_handler.TestInstanceLauncher()
        self.test_db_handler.create_full_instance(db_conf=self.test_db_conf, dist_conf=self.dist_conf, fe_conf=self.fe_conf)

        # Create database handler from test instance
        self.db_handler = self.test_db_handler.db_handler
        self.picture_hasher = picture_hasher.Picture_Hasher(self.fe_conf)
        self.picture_orber = picture_orber.Picture_Orber(self.fe_conf)

        # Construct a worker and overwrite link to redis db
        self.db_adder = database_adder.Database_Adder(self.test_db_conf, self.dist_conf, self.fe_conf)
        self.distance_engine = distance_engine.Distance_Engine(self.db_adder, self.test_db_conf, self.dist_conf, self.fe_conf)

    def set_decode_redis(self):
        test_db = redis.Redis(unix_socket_path=self.db_handler.get_socket_path('test'), decode_responses=True)
        self.distance_engine.storage_db = test_db
        self.db_adder.storage_db = test_db

    def set_raw_redis(self):
        test_db = redis.Redis(unix_socket_path=self.db_handler.get_socket_path('test'), decode_responses=False)
        self.distance_engine.storage_db = test_db
        self.db_adder.storage_db = test_db

    def tearDown(self):
        # Launch shutdown AND FLUSH script
        print("[TESTS] STOPPING DATABASE AS TEST : NOTHING WILL BE REMOVED ON STORAGE OR CACHE DATABASES [TESTS]")
        self.test_db_handler.tearDown()

    # ==================== ------ CLUSTER LIST ------- ====================

    def test_get_cluster_list(self):
        cluster_name_1 = "myperfectuuid"
        cluster_name_2 = "myperfectuuid_2"

        # Check cluster list
        tmp_list = self.db_adder.db_utils.get_cluster_list()
        self.assertEqual(len(tmp_list), 0)

        # Add cluster
        self.db_adder.db_utils.add_cluster(cluster_name_1)

        # Check for new cluster list
        tmp_list = self.db_adder.db_utils.get_cluster_list()
        self.assertEqual(len(tmp_list), 1)
        self.logger.debug(tmp_list)
        self.assertEqual(set([cluster_name_1]).issubset(tmp_list), True)

        # Add cluster
        self.db_adder.db_utils.add_cluster(cluster_name_2)

        # Check for new cluster list
        tmp_list = self.db_adder.db_utils.get_cluster_list()
        self.assertEqual(len(tmp_list), 2)
        self.logger.debug(tmp_list)
        self.assertEqual(set([cluster_name_2]).issubset(tmp_list), True)

    def test_add_cluster(self):
        cluster_name_1 = "myperfectuuid"
        cluster_name_2 = "myperfectuuid_2"

        # Check for cluster list
        tmp_list = self.db_adder.db_utils.get_cluster_list()
        self.assertEqual(len(tmp_list), 0)

        # Add cluster
        self.db_adder.db_utils.add_cluster(cluster_name_1)

        # Check for new cluster list
        tmp_list = self.db_adder.db_utils.get_cluster_list()
        self.assertEqual(len(tmp_list), 1)

        self.db_adder.db_utils.add_cluster(cluster_name_1)
        self.db_adder.db_utils.add_cluster(cluster_name_1)

        # Check for new cluster list
        tmp_list = self.db_adder.db_utils.get_cluster_list()
        self.assertEqual(len(tmp_list), 1)

        self.db_adder.db_utils.add_cluster(cluster_name_2)
        self.db_adder.db_utils.add_cluster(cluster_name_2)
        self.db_adder.db_utils.add_cluster(cluster_name_1)
        self.db_adder.db_utils.add_cluster(cluster_name_2)

        # Check for new cluster list
        tmp_list = self.db_adder.db_utils.get_cluster_list()
        self.assertEqual(len(tmp_list), 2)

    def test_rem_cluster(self):
        cluster_name_1 = "myperfectuuid"
        # cluster_name_2 = "myperfectuuid_2"

        # Check for cluster list
        tmp_list = self.db_adder.db_utils.get_cluster_list()
        self.assertEqual(len(tmp_list), 0)

        # Add cluster
        self.db_adder.db_utils.add_cluster(cluster_name_1)

        # Check for new cluster list
        tmp_list = self.db_adder.db_utils.get_cluster_list()
        self.assertEqual(len(tmp_list), 1)

        self.db_adder.db_utils.add_cluster(cluster_name_1)
        self.db_adder.db_utils.rem_cluster(cluster_name_1)

        # Check for new cluster list
        tmp_list = self.db_adder.db_utils.get_cluster_list()
        self.assertEqual(len(tmp_list), 0)

        # Add cluster
        self.db_adder.db_utils.add_cluster(cluster_name_1)

        # Check for new cluster list
        tmp_list = self.db_adder.db_utils.get_cluster_list()
        self.assertEqual(len(tmp_list), 1)

        self.db_adder.db_utils.rem_cluster(cluster_name_1)
        self.db_adder.db_utils.rem_cluster(cluster_name_1)

        # Check for new cluster list
        tmp_list = self.db_adder.db_utils.get_cluster_list()
        self.assertEqual(len(tmp_list), 0)

    # ==================== ------ ADDERS ------- ====================

    def get_descriptors(self, filename="original.bmp"):
        self.algo = cv2.ORB_create(nfeatures=10)
        orb_pic = cv2.imread(str(self.test_file_path / filename), 0)

        key_points, descriptors = self.algo.detectAndCompute(orb_pic, None)

        return key_points, descriptors

    def test_add_picture_to_storage(self):
        id_to_process = str(42)
        list_keypoints = self.get_descriptors()
        data_to_store = {"img": "MyPerfectPicture", "test": "test_value", "keypoints": list_keypoints}
        print("Stored :", data_to_store)
        self.set_raw_redis()

        # Add picture to storage
        self.db_adder.add_picture_to_storage(self.db_adder.storage_db_no_decode, id_to_process, data_to_store)

        # Get back data
        stored = self.db_adder.get_dict_from_key(self.db_adder.db_utils.db_access_no_decode, id_to_process, pickle=True)
        print("Fetched :", stored)

        # Checks
        self.assertEqual(data_to_store["img"], stored["img"])
        self.assertEqual(data_to_store["test"], stored["test"])
        self.assertEqual(len(data_to_store["keypoints"]), len(stored["keypoints"]))
        self.assertEqual(type(data_to_store["keypoints"][0]), type(stored["keypoints"][0]))

    def test_add_picture_to_cluster(self):

        cluster_name_1 = "myperfectuuid_1"
        cluster_name_2 = "myperfectuuid_2"

        image_id_1 = "myimageid_1"
        image_id_2 = "myimageid_2"

        pic_list = self.db_adder.db_utils.get_pictures_of_cluster(cluster_name_1)
        self.assertEqual(len(pic_list), 0)

        self.db_adder.db_utils.add_picture_to_cluster(image_id_1, cluster_name_1)
        pic_list = self.db_adder.db_utils.get_pictures_of_cluster(cluster_name_1)
        self.assertEqual(len(pic_list), 1)

        self.db_adder.db_utils.add_cluster(cluster_name_1)
        self.db_adder.db_utils.add_picture_to_cluster(image_id_1, cluster_name_1)
        pic_list = self.db_adder.db_utils.get_pictures_of_cluster(cluster_name_1)
        self.assertEqual(len(pic_list), 1)

        self.db_adder.db_utils.add_cluster(cluster_name_1)
        self.db_adder.db_utils.add_picture_to_cluster(image_id_2, cluster_name_1)
        self.db_adder.db_utils.add_picture_to_cluster(image_id_2, cluster_name_2)
        pic_list = self.db_adder.db_utils.get_pictures_of_cluster(cluster_name_1)
        self.assertEqual(len(pic_list), 2)

    def test_add_picture_to_new_cluster(self):
        image_id_1 = "myimageid_1"
        image_id_2 = "myimageid_2"

        cluster_name = self.db_adder.db_utils.add_picture_to_new_cluster(image_id_1)
        pic_list = self.db_adder.db_utils.get_pictures_of_cluster(cluster_name)
        self.assertEqual(len(pic_list), 1)

        cluster_name = self.db_adder.db_utils.add_picture_to_new_cluster(image_id_1)
        pic_list = self.db_adder.db_utils.get_pictures_of_cluster(cluster_name)
        self.assertEqual(len(pic_list), 1)

        self.db_adder.db_utils.add_picture_to_cluster(image_id_2, cluster_name)
        pic_list = self.db_adder.db_utils.get_pictures_of_cluster(cluster_name)
        self.assertEqual(len(pic_list), 2)

    def test_get_setname_of_cluster(self):
        val = self.db_adder.db_utils.get_setname_of_cluster("test")
        self.assertEqual(val, "test|pics")

    def test_is_feature_adding_list_empty(self):
        self.logger.debug("CHECKING EMPTY LIST")
        val = self.db_adder.is_feature_adding_list_empty(self.db_adder.storage_db_no_decode)
        self.assertTrue(val)
        binary_file = open(str(self.test_file_path / "original.bmp"), "rb")
        image = binary_file.read()

        self.logger.debug("ADDING STUFF")
        self.db_adder.add_to_queue(self.db_adder.cache_db_decode, queue_name=QueueNames.FEATURE_TO_ADD, id="my1", dict_to_store={"img": image})
        self.db_adder.add_to_queue(self.db_adder.cache_db_decode, queue_name=QueueNames.FEATURE_TO_ADD, id="my2", dict_to_store={"img": image})
        self.db_adder.add_to_queue(self.db_adder.cache_db_decode, queue_name=QueueNames.FEATURE_TO_ADD, id="my3", dict_to_store={"img": image})
        self.db_adder.add_to_queue(self.db_adder.cache_db_decode, queue_name=QueueNames.FEATURE_TO_ADD, id="my4", dict_to_store={"img": image})
        self.db_adder.add_to_queue(self.db_adder.cache_db_decode, queue_name=QueueNames.FEATURE_TO_ADD, id="my5", dict_to_store={"img": image})

        self.logger.debug("CHECKING EMPTY LIST")
        val = self.db_adder.is_feature_adding_list_empty(self.db_adder.storage_db_no_decode)
        self.assertFalse(val)

        self.logger.debug("WAITING")
        time.sleep(5)

        self.logger.debug("CHECKING EMPTY LIST")
        val = self.db_adder.is_feature_adding_list_empty(self.db_adder.storage_db_no_decode)
        self.assertFalse(val)

    def test_is_feature_request_list_empty(self):
        self.logger.debug("CHECKING EMPTY LIST")
        val = self.db_adder.is_feature_request_list_empty(self.db_adder.storage_db_no_decode)
        self.assertTrue(val)
        binary_file = open(str(self.test_file_path / "original.bmp"), "rb")
        image = binary_file.read()

        self.logger.debug("ADDING STUFF")
        self.db_adder.add_to_queue(self.db_adder.cache_db_decode, queue_name=QueueNames.FEATURE_TO_REQUEST, id="my1", dict_to_store={"img": image})
        self.db_adder.add_to_queue(self.db_adder.cache_db_decode, queue_name=QueueNames.FEATURE_TO_REQUEST, id="my2", dict_to_store={"img": image})
        self.db_adder.add_to_queue(self.db_adder.cache_db_decode, queue_name=QueueNames.FEATURE_TO_REQUEST, id="my3", dict_to_store={"img": image})
        self.db_adder.add_to_queue(self.db_adder.cache_db_decode, queue_name=QueueNames.FEATURE_TO_REQUEST, id="my4", dict_to_store={"img": image})
        self.db_adder.add_to_queue(self.db_adder.cache_db_decode, queue_name=QueueNames.FEATURE_TO_REQUEST, id="my5", dict_to_store={"img": image})

        self.logger.debug("CHECKING EMPTY LIST")
        val = self.db_adder.is_feature_request_list_empty(self.db_adder.storage_db_no_decode)
        self.assertFalse(val)

        self.logger.debug("WAITING")
        time.sleep(5)

        self.logger.debug("CHECKING EMPTY LIST")
        val = self.db_adder.is_feature_request_list_empty(self.db_adder.storage_db_no_decode)
        self.assertFalse(val)

    def test_is_request_list_empty(self):
        self.logger.debug("CHECKING EMPTY LIST")
        val = self.db_adder.is_request_list_empty(self.db_adder.storage_db_no_decode)
        self.assertTrue(val)

        binary_file = open(str(self.test_file_path / "original.bmp"), "rb")
        image = binary_file.read()

        self.logger.debug("ADDING STUFF")
        self.db_adder.add_to_queue(self.db_adder.cache_db_no_decode, queue_name=QueueNames.DB_TO_REQUEST, id="my1", dict_to_store={"A-HASH": "XXXX"}, pickle=True)
        self.db_adder.add_to_queue(self.db_adder.cache_db_no_decode, queue_name=QueueNames.DB_TO_REQUEST, id="my2", dict_to_store={"A-HASH": "XXXX"}, pickle=True)
        self.db_adder.add_to_queue(self.db_adder.cache_db_no_decode, queue_name=QueueNames.DB_TO_REQUEST, id="my3", dict_to_store={"A-HASH": "XXXX"}, pickle=True)
        self.db_adder.add_to_queue(self.db_adder.cache_db_no_decode, queue_name=QueueNames.DB_TO_REQUEST, id="my4", dict_to_store={"A-HASH": "XXXX"}, pickle=True)
        self.db_adder.add_to_queue(self.db_adder.cache_db_no_decode, queue_name=QueueNames.DB_TO_REQUEST, id="my5", dict_to_store={"A-HASH": "XXXX"}, pickle=True)

        self.logger.debug("CHECKING EMPTY LIST")
        val = self.db_adder.is_request_list_empty(self.db_adder.storage_db_no_decode)
        self.assertFalse(val)

        self.logger.debug("WAITING")
        time.sleep(5)

        self.logger.debug("CHECKING EMPTY LIST")
        val = self.db_adder.is_request_list_empty(self.db_adder.storage_db_no_decode)
        self.assertTrue(val)

    def test_is_adding_list_empty(self):
        self.logger.debug("CHECKING EMPTY LIST")
        val = self.db_adder.is_adding_list_empty(self.db_adder.storage_db_no_decode)
        self.assertTrue(val)

        binary_file = open(str(self.test_file_path / "original.bmp"), "rb")
        image = binary_file.read()

        self.logger.debug("ADDING STUFF")
        self.db_adder.add_to_queue(self.db_adder.cache_db_no_decode, queue_name=QueueNames.DB_TO_ADD, id="my1", dict_to_store={"A-HASH": "XXXX"}, pickle=True)
        self.db_adder.add_to_queue(self.db_adder.cache_db_no_decode, queue_name=QueueNames.DB_TO_ADD, id="my2", dict_to_store={"A-HASH": "XXXX"}, pickle=True)
        self.db_adder.add_to_queue(self.db_adder.cache_db_no_decode, queue_name=QueueNames.DB_TO_ADD, id="my3", dict_to_store={"A-HASH": "XXXX"}, pickle=True)
        self.db_adder.add_to_queue(self.db_adder.cache_db_no_decode, queue_name=QueueNames.DB_TO_ADD, id="my4", dict_to_store={"A-HASH": "XXXX"}, pickle=True)
        self.db_adder.add_to_queue(self.db_adder.cache_db_no_decode, queue_name=QueueNames.DB_TO_ADD, id="my4", dict_to_store={"A-HASH": "XXXX"}, pickle=True)

        self.logger.debug("CHECKING EMPTY LIST")
        val = self.db_adder.is_adding_list_empty(self.db_adder.storage_db_no_decode)
        self.assertFalse(val)

        self.logger.debug("WAITING")
        time.sleep(5)

        self.logger.debug("CHECKING EMPTY LIST")
        val = self.db_adder.is_adding_list_empty(self.db_adder.storage_db_no_decode)
        self.assertTrue(val)

    def test_change_picture_score(self):
        image_id_1 = "myimageid_1"

        cluster_name = self.db_adder.db_utils.add_picture_to_new_cluster(image_id_1)
        pic_list = self.db_adder.db_utils.get_pictures_of_cluster(cluster_name, with_score=True)
        self.logger.info(pic_list)

        self.assertEqual(len(pic_list), 1)
        self.assertEqual(pic_list[0][1], 100.0)

        self.db_adder.db_utils.update_picture_score_of_cluster(cluster_name, pic_list[0][0], 1)
        pic_list = self.db_adder.db_utils.get_pictures_of_cluster(cluster_name, with_score=True)
        self.logger.info(pic_list)

        self.assertEqual(len(pic_list), 1)
        self.assertEqual(pic_list[0][1], 1.0)

    def upload_picture(self, filename):
        # Upload a picture and returns an id
        id_to_process = filename + "ID"

        with open(str(self.test_file_path / filename), "rb") as binary_file:
            # Read the whole file at once
            image = binary_file.read()
            # image = open(str(self.test_file_path/filename), "rb")

            # Get hash values of picture
            hash_dict = self.picture_hasher.hash_picture(image)
            self.logger.debug(f"Computed hashes : {hash_dict}")

            # Get ORB values of picture
            orb_dict = self.picture_orber.orb_picture(image)
            self.logger.debug(f"Computed orb values : {orb_dict}")

            # Merge dictionaries
            merged_dict = {**hash_dict, **orb_dict}
            self.logger.debug(f"To send to db dict : {merged_dict}")

            self.db_adder.add_picture_to_storage(self.db_adder.storage_db_no_decode, id_to_process, merged_dict)

            # Get back data (sanity)
            stored = self.db_adder.get_dict_from_key(self.db_adder.db_utils.db_access_no_decode, id_to_process, pickle=True)
            print("Fetched :", stored)

            return id_to_process

    def test_reevaluate_representative_picture_order(self):
        # Add pictures to storage
        self.set_raw_redis()

        id = self.upload_picture("original.bmp")
        cluster_id = self.db_adder.db_utils.add_picture_to_new_cluster(id)

        for file in ["green.bmp", "blue.bmp", "dark.bmp", "negative_dark.bmp", "yellow.bmp"]:
            id_to_process = self.upload_picture(file)

            # Add picture to storage
            self.db_adder.db_utils.add_picture_to_cluster(id_to_process, cluster_id)

        # Performs the reevaluation
        self.db_adder.reevaluate_representative_picture_order(cluster_id)

        # Get back pictures of the cluster
        pic_list = self.db_adder.db_utils.get_pictures_of_cluster(cluster_id, with_score=True)
        self.logger.info(pic_list)

        self.assertEqual(pic_list[0][0], "original.bmpID")  # The most representative picture is the original one

    def test_reevaluate_representative_picture_order_per_add(self):
        # Add pictures to storage
        self.set_raw_redis()

        id = self.upload_picture("original.bmp")
        cluster_id = self.db_adder.db_utils.add_picture_to_new_cluster(id)
        self.logger.warning(f"Adding ... original as {id}")

        self.logger.warning(f"TETS > Reevaluating representative picture ... {id}")
        # Performs the reevaluation
        self.db_adder.reevaluate_representative_picture_order(cluster_id, id)

        self.logger.warning(f"TETS > Check all pictures of cluster ... {id}")
        # Get back pictures of the cluster
        pic_list = self.db_adder.db_utils.get_pictures_of_cluster(cluster_id, with_score=True)
        self.logger.info(pic_list)

        for file in ["green.bmp", "blue.bmp", "dark.bmp", "negative_dark.bmp", "yellow.bmp"]:
            self.logger.warning(f"TETS > Adding ... {file}")
            id_to_process = self.upload_picture(file)

            self.logger.warning(f"TETS > Add picture to cluster ... {file}")
            # Add picture to storage
            self.db_adder.db_utils.add_picture_to_cluster(id_to_process, cluster_id)

            self.logger.warning(f"TETS > Reevaluating representative picture ... {file}")
            # Performs the reevaluation
            self.db_adder.reevaluate_representative_picture_order(cluster_id, id_to_process)

            self.logger.warning(f"TETS > Check all pictures of cluster ... {file}")
            # Get back pictures of the cluster
            pic_list = self.db_adder.db_utils.get_pictures_of_cluster(cluster_id, with_score=True)
            self.logger.info(pic_list)

        self.assertEqual(pic_list[0][0], "original.bmpID")  # The most representative picture is the original one

    def test_absolute_truth_and_meaning(self):
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
