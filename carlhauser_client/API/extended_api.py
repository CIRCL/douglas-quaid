#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging.config
# ==================== ------ STD LIBRARIES ------- ====================
import os
import pathlib
import sys
from typing import Dict, List
import collections
import time

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))
from carlhauser_client.Helpers.environment_variable import get_homedir
from carlhauser_client.API.simple_api import Simple_API

from common.Graph.graph_datastructure import GraphDataStruct


# ==================== ------ LAUNCHER ------- ====================
class Extended_API(Simple_API):
    # Provides "Higher-level" API calls

    def __init__(self, url, certificate_path):
        super().__init__(url, certificate_path)

    def add_pictures_to_db(self, image_folder: pathlib.Path) -> (dict, int):
        # Upload pictures to Redis Database (douglas Quaid API) and
        # return a mapping (filename-> ID provided by server) and the number of pictures successfuly uploaded

        ID_mapping_old_to_new = {}
        nb_pictures = 0

        self.logger.debug(f"Sending pictures of {image_folder} in the DB.")
        # Add pictures to DB, create mapping OLD NAME -> NEW NAME (or opposite)
        for image_path in image_folder.iterdir():
            if image_path.is_file():
                # Upload the image to db
                res = self.add_picture_server(image_path)
                if res[0] == True:
                    # The upload had been successful
                    ID_mapping_old_to_new[image_path.name] = res[1]

                    self.logger.info(f"Mapping from {image_path.name} to {res[1]}")
                    nb_pictures += 1
                else:
                    self.logger.error(f"Error during upload of {image_path.name} : {res[1]}")

        return ID_mapping_old_to_new, nb_pictures

    def request_similar_and_wait(self, image_path: pathlib.Path, waittime=60):
        start = time.time()
        self.logger.debug(f"Requesting similar pictures to {image_path}")
        is_success, request_id = self.request_picture_server(image_path)

        if is_success:
            self.logger.debug(f"Request successful. Waiting for results.")
            is_success = self.poll_until_result_ready(request_id, max_time=waittime)

            if is_success:
                self.logger.debug(f"Request executed. Fetching results.")
                is_success, results = self.retrieve_request_results(request_id)

                if is_success:
                    results["request_time"] = time.time() - start
                    self.logger.info(f"Request answered in : {results['request_time']}")
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

    def request_pictures(self, image_folder: pathlib.Path) -> (dict, int):
        # Upload pictures to Redis Database (douglas Quaid API) and
        # return a mapping (filename-> ID provided by server) and the number of pictures successfully uploaded

        request_answers = []
        nb_pictures = 0

        self.logger.debug(f"Requesting similar pictures of {image_folder} to the DB.")
        # Add picture to be requested
        for image_path in image_folder.iterdir():
            if image_path.is_file():
                # Upload the image to db
                try :
                    results = self.request_similar_and_wait(image_path)
                    request_answers.append(results)
                    self.logger.debug(f"Successfully requested {image_path.name}.")
                    nb_pictures += 1

                except Exception as e :
                    self.logger.error(f"Error occurred during {image_path.name} request : {e}.")

        return request_answers, nb_pictures


    def get_db_dump_as_graph(self) -> GraphDataStruct:
        # Ask the DB to provide a dump of its actual state (douglas Quaid API) and
        # return a graphe (common datastructure) representation of it

        # Dump DB as graphe / clusters
        is_success, db = self.export_db_server()

        if is_success:
            print(f"Database fetched successfully.")
            # The upload had been successful
            graphe_struct = GraphDataStruct.load_from_dict(db)
        else:
            raise Exception(f"Error during db dump of {db}")

        return graphe_struct

    @staticmethod
    def get_api():
        return Extended_API.get_custom_api(Extended_API)

    # ========= UTILITIES =============

    @staticmethod
    def copy_id_to_image(dict_to_modify):

        for i in dict_to_modify['clusters']:
            i["image"] = "anchor.png"
            i["shape"] = "icon"
        for i in dict_to_modify['nodes']:
            i["image"] = i["id"]

        return dict_to_modify

    @staticmethod
    def apply_revert_mapping(dict_to_modify, mapping):
        # Modify all occurences in dict_to_modify of keys-values in mapping, by their value
        # Ex : {"toto":"tata"}, {"tata":"new"} ==> {"toto":"new"}
        return update_values_dict(dict_to_modify, {}, mapping)

    @staticmethod
    def revert_mapping(mapping: Dict) -> Dict:
        # Revert the value/keys of a dictionnary
        return {v: k for k, v in mapping.items()}


def update_values_dict(original_dict, future_dict, new_mapping):
    # Recursively updates values of a nested dict by performing recursive calls
    # Replace in <original_dict> all keys elements present in <new_mapping> by their value in <new_mapping>
    # Ex : {"toto":"tata"}, {"tata":"new"} ==> {"toto":"new"}

    if isinstance(original_dict, Dict):
        # It's a dict
        tmp_dict = {}
        for key, value in original_dict.items():
            tmp_dict[key] = update_values_dict(value, future_dict, new_mapping)
        return tmp_dict
    elif isinstance(original_dict, List):
        # It's a List
        tmp_list = []
        for i in original_dict:
            tmp_list.append(update_values_dict(i, future_dict, new_mapping))
        return tmp_list
    else:
        # It's not a dict, maybe a int, a string, etc. so we replace it with what is needed
        return original_dict if original_dict not in new_mapping else new_mapping[original_dict]
