#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging.config
# ==================== ------ STD LIBRARIES ------- ====================
import os
import pathlib
import sys
import time

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))
from carlhauser_client.Helpers.environment_variable import get_homedir
from carlhauser_client.API.carlhauser_client import API_caller
from carlhauser_client.Evaluator.cluster_matcher import Cluster_matcher
from carlhauser_client.Evaluator.performance_evaluation import Performance_Evaluator
from carlhauser_client.Evaluator.confusion_matrix_generator import ConfusionMatrixGenerator
import carlhauser_server.Helpers.json_import_export as json_import_export
from pprint import pformat

from common.Graph.graph_datastructure import GraphDataStruct, merge_graphs

# from . import helpers

# ==================== ------ PREPARATION ------- ====================
# load the logging configuration
logconfig_path = (get_homedir() / pathlib.Path("carlhauser_client", "logging.ini")).resolve()
logging.config.fileConfig(str(logconfig_path))


# ==================== ------ LAUNCHER ------- ====================
class Evaluator():
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.API = self.get_api()

    def launch(self, image_folder: pathlib.Path, visjs_json_path: pathlib.Path, output_path: pathlib.Path):
        # Compute a complete run of the library on a folder, with a ground truth file, to compute metrics about the quality of the matching
        # return metric

        # ========= MANUAL EVALUATION =========

        if visjs_json_path is None:
            raise Exception(f"VisJS ground truth path not set. Impossible to evaluate.")
        else:
            # 1. Load pictures to visjs = node server.js -i ./../douglas-quaid/datasets/MINI_DATASET/ -t ./TMP -o ./TMP
            # 2. Cluster manually pictures in visjs = < Do manual stuff>
            # 3. Load json graphe
            visjs = json_import_export.load_json(visjs_json_path)
            visjs = GraphDataStruct.load_from_dict(visjs)

        # ========= AUTO EVALUATION =========
        # Send pictures to DB and get id mapping
        mapping_old_filename_to_new_id, nb_pictures = self.add_pictures_to_db(image_folder)
        time.sleep(10)  # Let time to add pictures to db

        # Get a DB dump
        db_dump = self.get_db_dump_as_graph()

        # ========= COMPARISON =========
        # Apply name mapping to dict (find back original names)
        visjs.replace_id_from_mapping(mapping_old_filename_to_new_id)

        # Get only list of clusters
        candidate = db_dump.get_clusters()
        original = visjs.get_clusters()

        # Match clusters
        # 1. Manually ? (Go back to visjs + rename)
        # 2. Automatically ? (Number of common elements ~)
        matcher = Cluster_matcher()
        matching = matcher.match_clusters(original, candidate)  # Matching original + Candidate ==> Group them per pair

        # Compute performance regarding input graphe
        perf_eval = Performance_Evaluator()
        matching_with_perf = perf_eval.evaluate_performance(matching, nb_pictures)  # pair of clusters ==> Quality score for each

        # Store performance in a file
        save_path_perf = output_path / "perf.json"
        perf_overview = perf_eval.save_perf_results(save_path_perf)

        # ========= RESULT VISUALIZATON =========

        # Convert matching with performance to confusion matrix
        matrix_creator = ConfusionMatrixGenerator()
        matrix_creator.create_and_export_confusion_matrix(original, candidate, matching, output_path / "matrix.pdf")  # Matching original + Candidate ==> Group them per pair

        # Convert dumped graph to visjs graphe
        # ==> red if linked made by algo, but non existant + Gray, true link that should have been created (
        # ==> Green if linked made by algo and existant
        save_path_json = output_path / "merged_graph.json"
        output_graph = merge_graphs(visjs, db_dump, matching)
        json_import_export.save_json(output_graph, save_path_json)
        self.logger.debug(f"DB Dump json saved in : {save_path_json}")

        # ==============================

        return perf_overview

    def add_pictures_to_db(self, image_folder: pathlib.Path) -> (dict, int):
        # Upload pictures to Redis Database (douglas Quaid API) and
        # return a mapping (filename-> ID provided by server) and the number of pictures successfuly uploaded

        ID_mapping_old_to_new = {}
        nb_pictures = 0

        # Add pictures to DB, create mapping OLD NAME -> NEW NAME (or opposite)
        for image_path in image_folder.iterdir():
            if image_path.is_file():
                # Upload the image to db
                res = self.API.add_picture_server(image_path)
                if res[0] == True:
                    # The upload had been successful
                    ID_mapping_old_to_new[image_path.name] = res[1]

                    self.logger.info(f"Mapping from {image_path.name} to {res[1]}")
                    nb_pictures += 1
                else:
                    self.logger.error(f"Error during upload of {image_path.name} : {res[1]}")

        return ID_mapping_old_to_new, nb_pictures


    def get_db_dump_as_graph(self) -> GraphDataStruct:
        # Ask the DB to provide a dump of its actual state (douglas Quaid API) and
        # return a graphe (common datastructure) representation of it

        # Dump DB as graphe / clusters
        res = self.API.export_db_server()

        if res[0] == True:
            # The upload had been successful
            graphe_struct = GraphDataStruct.load_from_dict(res[1])
        else:
            raise Exception(f"Error during db dump of {res}")

        return graphe_struct

    def get_api(self):
        # Generate the API access point link to the hardcoded server
        cert = (get_homedir() / "carlhauser_client" / "cert.pem").resolve()

        # See : https://stackoverflow.com/questions/10667960/python-requests-throwing-sslerror
        # To create : openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
        api = API_caller(url='https://localhost:5000/', certificate_path=cert)  # TODO : Should be =cert
        logging.captureWarnings(True)  # TODO : Remove
        return api


if __name__ == '__main__':
    evaluator = Evaluator()
    image_folder = get_homedir() / "datasets" / "MINI_DATASET"
    gt = get_homedir() / "datasets" / "MINI_DATASET_VISJS.json"
    output_path =  get_homedir() / "carlhauser_client"
    evaluator.launch(image_folder, gt, output_path)
