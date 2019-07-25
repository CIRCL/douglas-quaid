#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pathlib
import time
from typing import Dict, List

import common.ImportExport.json_import_export as json_import_export
from common.environment_variable import get_homedir
import carlhauser_client.Helpers.dict_utilities as dict_utilities
from carlhauser_client.API.simple_api import Simple_API
from common.Graph.graph_datastructure import GraphDataStruct
from common.environment_variable import load_client_logging_conf_file
from pprint import pformat

load_client_logging_conf_file()


# ==================== ------ LAUNCHER ------- ====================
class Extended_API(Simple_API):
    '''
    Provides "Higher-level" API calls
    '''

    def __init__(self, url, certificate_path):
        super().__init__(url, certificate_path)

    @staticmethod
    def get_api():
        """
        Static method that return an instance of the API (ExtendedAPI type)
        :return: Extended API instance
        """
        return Extended_API.get_custom_api(Extended_API)

    # ========= UTILITIES =============
    # ================= ADD PICTURES =================

    def add_one_picture_and_wait(self, image_path: pathlib.Path, max_time: int = 60) -> (bool, str):
        """
        Add a picture to the server, wait for the adding to be performed.
        :param image_path: the path of the picture to add
        :param max_time: maximum allowed time to wait before timing out. By default -1 = No time out
        :return: boolean : True if the picture had successfuly been added, False otherwise , and the server_id of the sent picture
        """

        # Starting count-down
        start = time.time()

        # Requesting the result
        self.logger.debug(f"Adding picture {image_path}")
        is_success, img_id = self.add_one_picture(image_path)

        # Managing the answer
        if is_success:
            self.logger.debug(f"Adding successful. Waiting for adding to complete.")
            is_success = self.poll_until_adding_done(max_time=max_time)

            if is_success:
                self.logger.info(f"Adding executed in : {time.time() - start}s")
                return is_success, img_id
            else:
                self.logger.error(f"Error on adding status polling.")
                raise Exception("Error on adding status polling.")
        else:
            self.logger.error(f"Error on adding sending.")
            raise Exception("Error on adding sending.")

    def add_many_pictures_no_wait(self, image_folder: pathlib.Path) -> (Dict[str, str], int):
        """
        Add all the pictures of the provided folder to the server (direct children, not recursive)
        :param image_folder: path to the folder of pictures
        :return: Mapping (filename-> ID provided by server) and the number of pictures successfuly uploaded
        """

        return self._add_many_pictures_with(image_folder, self.add_one_picture)

    def add_many_picture_and_wait_for_each(self, image_folder: pathlib.Path) -> (Dict[str, str], int):
        """
        Add all the pictures of the provided folder to the server (direct children, not recursive)
        wait for each of them to be added (one after the other)
        :param image_folder: path to the folder of pictures
        :return: Mapping (filename-> ID provided by server) and the number of pictures successfully uploaded
        """

        return self._add_many_pictures_with(image_folder, self.add_one_picture_and_wait)

    def add_many_pictures_and_wait_global(self, image_folder: pathlib.Path) -> (Dict[str, str], int):
        """
        Add all the pictures at once of the provided folder to the server (direct children, not recursive)
        and then wait for ALL of them to be added (as a batch). Faster than add_many_pictures_and_wait
        :param image_folder: path to the folder of pictures
        :return: Mapping (filename-> ID provided by server) and the number of pictures successfully uploaded
        """

        mapping, nb_pics_sent = self._add_many_pictures_with(image_folder, self.add_one_picture)

        self.logger.info(f"Pictures all sent to server ... waiting for adding complete.")
        start = time.time()
        is_success = self.poll_until_adding_done(max_time=-1)

        if is_success:
            self.logger.info(f"Adding executed in : {time.time() - start}s after all pictures sent")
        else:
            self.logger.error(f"Error on adding status polling.")
            raise Exception("Error on adding status polling.")

        return mapping, nb_pics_sent

    def _add_many_pictures_with(self, image_folder: pathlib.Path, function) -> (Dict[str, str], int):
        """
        Generic function to send pictures calling the "function". Internal use for factorization
        :param image_folder: path to the folder of pictures
        :param function: Mapping (filename-> ID provided by server) and the number of pictures successfuly uploaded
        :return:
        """
        self.logger.debug(f"Sending pictures of {image_folder} in the DB.")
        mapping_filename_to_id = {}
        nb_pics_sent = 0

        # For all pictures (direct children of the folder)
        for image_path in image_folder.iterdir():
            if image_path.is_file():
                self.logger.debug(f"Found picture to be send : {image_path}.")

                # Upload the image to db
                success, server_id = function(image_path)  # Return picture id ! only !

                if success:
                    # The upload had been successful
                    self.logger.info(f"Mapping from {image_path.name} to {server_id}")
                    mapping_filename_to_id[image_path.name] = server_id
                    nb_pics_sent += 1
                else:
                    self.logger.error(f"Error during upload of {image_path.name} : {server_id}")

        return mapping_filename_to_id, nb_pics_sent

    # ================= REQUEST PICTURES AND WAITING =================

    def request_one_picture_and_wait(self, image_path: pathlib.Path, max_time: int = 60) -> Dict:
        '''
        Request similar picture of one picture to the server, wait for an answer.
        :param image_path: the path of the picture to request
        :param max_time: maximum allowed time to wait before timing out. By default -1 = No time out
        :return: the answer of the server. #TODO : Give an example of answer
        '''

        # Starting count-down
        start = time.time()

        # Requesting the result
        self.logger.debug(f"Requesting similar pictures to {image_path}")
        is_success, request_id = self.request_similar(image_path)

        # Managing the answer
        if is_success:
            self.logger.debug(f"Request successful. Waiting for results.")
            is_success = self.poll_until_result_ready(request_id, max_time=max_time)

            if is_success:
                self.logger.debug(f"Request executed. Fetching results.")
                is_success, results = self.get_results(request_id)

                if is_success:
                    results["request_time"] = time.time() - start
                    self.logger.info(f"Request answered in : {results['request_time']}s")
                    return results

                else:
                    self.logger.error(f"Error on results retrieval.")
                    raise Exception("Error on results retrieval.")
            else:
                self.logger.error(f"Error on results polling.")
                raise Exception("Error on results polling.")

        else:
            self.logger.error(f"Error on request sending.")
            raise Exception("Error on request sending.")

    def request_many_pictures_and_wait_for_each(self, image_folder: pathlib.Path) -> (dict, int):
        '''
        Request similar picture of all pictures of the provided folder to the server (direct children, not recursive)
        wait for each of them (one after the other) and store all the result in one unique list
        :param image_folder: path to the folder of pictures
        :return: A list of all answers, and the total number of pictures successfully requested
        '''

        self.logger.debug(f"Requesting similar pictures of {image_folder} to the DB.")
        list_answers = []
        nb_pics_requested = 0

        # Iterate over all picture directly child of the folder
        for image_path in image_folder.iterdir():
            if image_path.is_file():
                # Got one image to upload and wait for result

                try:
                    self.logger.debug(f"Working on picture #{nb_pics_requested}.")
                    results = self.request_one_picture_and_wait(image_path)

                    self.logger.debug(f"Successfully requested {image_path.name}.")
                    list_answers.append(results)
                    nb_pics_requested += 1

                except Exception as e:
                    self.logger.error(f"Error occurred during {image_path.name} request : {e}.")

        return list_answers, nb_pics_requested

    def request_many_pictures_and_wait_global(self, image_folder: pathlib.Path) -> (dict, int):
        '''
        Request similar picture of all pictures of the provided folder to the server (direct children, not recursive)
        wait for them AS A BATCH (wait the last one only), fetch and store all the results in one unique list
        :param image_folder: path to the folder of pictures
        :return: A list of all answers, and the total number of pictures successfully requested
        '''

        self.logger.debug(f"Requesting similar pictures of {image_folder} to the DB.")
        list_requests_id = []
        nb_pics_requested = 0
        list_answers = []

        # Iterate over all picture directly child of the folder
        for image_path in image_folder.iterdir():
            if image_path.is_file():

                # Got one image to upload
                try:
                    self.logger.debug(f"Working on picture #{nb_pics_requested}.")
                    is_success, request_id = self.request_similar(image_path)

                    self.logger.debug(f"Successfully requested {image_path.name}. Waiting to ask results")
                    list_requests_id.append(request_id)
                    nb_pics_requested += 1

                except Exception as e:
                    self.logger.error(f"Error occurred during {image_path.name} request : {e}.")

        # Wait until last requested picture is
        _ = self.poll_until_result_ready(list_requests_id[len(list_requests_id) - 1], max_time=-1)

        for request_id in list_requests_id:
            is_success, results = self.get_results(request_id)
            list_answers.append(results)

        return list_answers, nb_pics_requested

    # ================= EXPORT AND DUMP =================

    def get_db_dump_as_graph(self) -> GraphDataStruct:
        '''
        Ask the server a copy of the database, convert it as graphe and returns it
        :return: A graph datastructure of the server's storage
        '''

        # Dump DB as graphe / clusters
        is_success, db = self.export_db_server()

        if is_success:
            print(f"Database fetched successfully.")
            # The upload had been successful
            graphe_struct = GraphDataStruct.load_from_dict(db)
            return graphe_struct
        else:
            raise Exception(f"Error during db dump of {db}")

    # ================= ALL =================

    def add_and_request_and_dump_pictures(self, image_folder: pathlib.Path) -> List:
        '''
        Send pictures of a folder, request all pictures one by one, construct a list of results, revert the mapping to get back pictures names
        :param image_folder: The folder of images to send
        :return: The list of results
        '''

        self.logger.info("Automated launch : add pictures from folder, request all, and dump graph / list of results")

        # 1-  Send pictures to DB and get id mapping
        mapping_old_filename_to_new_id, nb_pictures = self.add_many_pictures_and_wait_global(image_folder)
        # add_many_pictures_and_wait_global
        # add_many_picture_and_wait_for_each

        # TODO : To remove , debug only
        json_import_export.save_json(mapping_old_filename_to_new_id, pathlib.Path(get_homedir() / "mapping_old_filename_to_new_id.json"))

        # 2 - Get a DB dump
        list_results, nb_pictures = self.request_many_pictures_and_wait_global(image_folder)
        # request_many_pictures_and_wait_global
        # request_many_pictures_and_wait_for_each

        # TODO : To remove , debug only
        json_import_export.save_json(list_results, pathlib.Path(get_homedir() / "list_result_before_reversion.json"))

        list_results = dict_utilities.apply_revert_mapping(list_results, mapping_old_filename_to_new_id)
        # TODO : do it with graphes ? graphe_struct.replace_id_from_mapping(mapping)

        # TODO : To remove , debug only
        json_import_export.save_json(list_results, pathlib.Path(get_homedir() / "list_result_after_reversion.json"))

        # We guarantee that each request is not None and each request has a request_id
        clean_list_results = [r for r in list_results if r is not None and r.get("request_id", None) is not None]

        if len(list_results) != len(clean_list_results):
            self.logger.critical(f"Errors during results fetching. {abs(len(list_results) - len(clean_list_results))} elements were null or without request id.")

        return clean_list_results
