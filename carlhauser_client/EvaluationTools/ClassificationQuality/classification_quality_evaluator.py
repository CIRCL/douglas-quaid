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
from carlhauser_client.API.extended_api import Extended_API
from carlhauser_client.EvaluationTools.ClassificationQuality.cluster_matcher import Cluster_matcher
from carlhauser_client.EvaluationTools.ClassificationQuality.cluster_matching_quality_evaluator import ClusterMatchingQualityEvaluator
from carlhauser_client.EvaluationTools.ClassificationQuality.confusion_matrix_generator import ConfusionMatrixGenerator
import carlhauser_server.Helpers.json_import_export as json_import_export

from common.Graph.graph_datastructure import GraphDataStruct, merge_graphs

# from . import helpers

# ==================== ------ PREPARATION ------- ====================
# load the logging configuration
logconfig_path = (get_homedir() / pathlib.Path("carlhauser_client", "logging.ini")).resolve()
logging.config.fileConfig(str(logconfig_path))


# ==================== ------ LAUNCHER ------- ====================
class ClassificationQualityEvaluator():
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.API = Extended_API.get_api()

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
        mapping_old_filename_to_new_id, nb_pictures = self.API.add_pictures_to_db(image_folder)
        time.sleep(10)  # Let time to add pictures to db

        # Get a DB dump
        db_dump = self.API.get_db_dump_as_graph()

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
        perf_eval = ClusterMatchingQualityEvaluator()
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


'''
def main():
    parser = argparse.ArgumentParser(description='Perform an evaluation on a dataset : Send all pictures, ')
    parser.add_argument('-p', '--path', dest='path', action='store', type=lambda p: pathlib.Path(p).absolute(), default=1, help='all path')
    parser.add_argument('--version', action='version', version='humanizer %s' % ("1.0.0"))

    args = parser.parse_args()
    humanizer = Humanizer()
    humanizer.rename_all_files(args.path)

'''


def test():
    evaluator = ClassificationQualityEvaluator()
    image_folder = get_homedir() / "datasets" / "MINI_DATASET"
    gt = get_homedir() / "datasets" / "MINI_DATASET_VISJS.json"
    output_path = get_homedir() / "carlhauser_client"
    evaluator.launch(image_folder, gt, output_path)


if __name__ == "__main__":
    test()
