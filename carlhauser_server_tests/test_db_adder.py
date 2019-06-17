# -*- coding: utf-8 -*-

import subprocess
import time
import unittest
import cv2
import pathlib

import redis
import logging

from carlhauser_server.Helpers.environment_variable import get_homedir
import carlhauser_server.Configuration.database_conf as database_conf
import carlhauser_server.Configuration.distance_engine_conf as distance_engine_conf
import carlhauser_server.Configuration.feature_extractor_conf as feature_extractor_conf
import carlhauser_server.DistanceEngine.distance_engine as distance_engine
import carlhauser_server.Helpers.database_start_stop as database_start_stop
import carlhauser_server.DatabaseAccessor.database_adder as database_adder
import os

import carlhauser_server.FeatureExtractor.picture_hasher as picture_hasher
import carlhauser_server.FeatureExtractor.picture_orber as picture_orber


class testDistanceEngine(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()
        # self.conf = .Default_configuration()
        self.test_file_path = get_homedir() / pathlib.Path("carlhauser_server_tests/test_DistanceEngine/")

        # Create configurations
        self.db_conf = database_conf.Default_database_conf()
        self.dist_conf = distance_engine_conf.Default_distance_engine_conf()
        self.fe_conf = feature_extractor_conf.Default_feature_extractor_conf()

        # Create database handler from configuration file
        self.db_handler = database_start_stop.Database_StartStop(conf=self.db_conf)
        self.picture_hasher = picture_hasher.Picture_Hasher(self.fe_conf)
        self.picture_orber = picture_orber.Picture_Orber(self.fe_conf)

        # Scripts overwrite
        self.db_handler.test_socket_path = get_homedir() / self.db_conf.DB_SOCKETS_PATH / 'test.sock'
        self.db_handler.launch_test_script_path = get_homedir() / self.db_conf.DB_SCRIPTS_PATH / "run_redis_test.sh"
        self.db_handler.shutdown_test_script_path = get_homedir() / self.db_conf.DB_SCRIPTS_PATH / "shutdown_redis_test.sh"

        # Construct a worker and overwrite link to redis db
        self.db_adder = database_adder.Database_Adder(self.db_conf, self.dist_conf, self.fe_conf)
        self.db_adder.db_utils.db_access_decode = redis.Redis(unix_socket_path=self.db_handler.get_socket_path('test'), decode_responses=True)
        self.db_adder.db_utils.db_access_no_decode = redis.Redis(unix_socket_path=self.db_handler.get_socket_path('test'), decode_responses=False)
        self.db_adder.storage_db_decode = redis.Redis(unix_socket_path=self.db_handler.get_socket_path('test'), decode_responses=True)
        self.db_adder.storage_db_no_decode = redis.Redis(unix_socket_path=self.db_handler.get_socket_path('test'), decode_responses=False)
        self.de = distance_engine.Distance_Engine(self.db_adder, self.db_conf, self.dist_conf, self.fe_conf)
        test_db = redis.Redis(unix_socket_path=self.db_handler.get_socket_path('test'), decode_responses=True)
        self.de.storage_db = test_db
        self.db_adder.storage_db = test_db

        # Launch test Redis DB
        if not self.db_handler.is_running('test'):
            subprocess.Popen([str(self.db_handler.launch_test_script_path)], cwd=self.db_handler.launch_test_script_path.parent)

        # Time for the socket to be opened
        time.sleep(1)

    def set_decode_redis(self):
        test_db = redis.Redis(unix_socket_path=self.db_handler.get_socket_path('test'), decode_responses=True)
        self.de.storage_db = test_db
        self.db_adder.storage_db = test_db

    def set_raw_redis(self):
        test_db = redis.Redis(unix_socket_path=self.db_handler.get_socket_path('test'), decode_responses=False)
        self.de.storage_db = test_db
        self.db_adder.storage_db = test_db

    def tearDown(self):
        # Shutdown test Redis DB
        if self.db_handler.is_running('test'):
            subprocess.Popen([str(self.db_handler.shutdown_test_script_path)], cwd=self.db_handler.test_socket_path.parent)

        # If start and stop are too fast, then it can't stop nor start, as it can't connect
        # e.g. because the new socket couldn't be create as the last one is still here
        time.sleep(1)

        # TODO : Kill subprocess ?

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
        assert True


if __name__ == '__main__':
    unittest.main()
