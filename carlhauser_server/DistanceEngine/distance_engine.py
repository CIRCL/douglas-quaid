#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import logging
from typing import List, Dict
from carlhauser_server.DistanceEngine.scoring_datastrutures import DecisionTypes as dt
import carlhauser_server.Configuration.database_conf as database_conf
import carlhauser_server.Configuration.distance_engine_conf as distance_engine_conf
import carlhauser_server.Configuration.feature_extractor_conf as feature_extractor_conf
import carlhauser_server.DatabaseAccessor.database_worker as database_worker
import carlhauser_server.DistanceEngine.distance_hash as distance_hash
import carlhauser_server.DistanceEngine.distance_orb as distance_orb
import carlhauser_server.DistanceEngine.distance_bow_orb as distance_bow_orb
import carlhauser_server.DistanceEngine.merging_engine as merging_engine
import carlhauser_server.DistanceEngine.scoring_datastrutures as scoring_datastrutures
from common.CustomException import AlgoFeatureNotPresentError
from common.environment_variable import load_server_logging_conf_file

load_server_logging_conf_file()


class Distance_Engine:
    """
    Handle distance computation between pictures and their representations.
    """

    def __init__(self, parent: database_worker, db_conf: database_conf.Default_database_conf, dist_conf: distance_engine_conf.Default_distance_engine_conf,
                 fe_conf: feature_extractor_conf.Default_feature_extractor_conf):
        # STD attributes
        self.logger = logging.getLogger(__name__)
        self.logger.info("... which is a Distance Engine")

        # Save configuration
        self.db_conf = db_conf
        self.dist_conf = dist_conf
        self.fe_conf = fe_conf

        # Reference to database worker parent to get accessors
        self.parent = parent

        # Create distance extractor
        self.distance_hash = distance_hash.Distance_Hash(db_conf, dist_conf, fe_conf)
        self.distance_orb = distance_orb.Distance_ORB(db_conf, dist_conf, fe_conf)
        self.distance_bow_orb = distance_bow_orb.Distance_BoW_ORB(db_conf, dist_conf, fe_conf)
        self.merging_engine = merging_engine.Merging_Engine(db_conf, dist_conf, fe_conf)

    # ==================== ------ INTER ALGO DISTANCE ------- ====================
    def get_dist_and_decision_algos_to_algos(self, pic_package_from: Dict, pic_package_to: Dict) -> Dict[str, scoring_datastrutures.AlgoMatch]:
        """
        Compute a list of distance and decision from two images representations, with activated (conf) algorithms.
        :param pic_package_from: dict of one image features
        :param pic_package_to: dict of one image features
        :return: merged dict of distance and decision for each algorithm
        """

        merged_dict = {}

        # Get hash distances
        try:
            hash_dict = self.distance_hash.hash_distance(pic_package_from, pic_package_to)
            self.logger.debug(f"Computed hashes distance : {hash_dict}")
            merged_dict.update(hash_dict)
        except AlgoFeatureNotPresentError as e:
            self.logger.warning(f"No feature present for hashing algorithms. Normal if HASHES is not activated in configuration. Error : {e}")

        # Get ORB distances
        try:
            orb_dict = self.distance_orb.orb_distance(pic_package_from, pic_package_to)
            self.logger.debug(f"Computed orb distance : {orb_dict}")
            merged_dict.update(orb_dict)
        except AlgoFeatureNotPresentError as e:
            self.logger.warning(f"No feature present for orbing algorithms. Normal if ORB is not activated in configuration. Error : {e}")

        # Get BoW-ORB distances
        try:
            bow_orb_dict = self.distance_bow_orb.bow_orb_distance(pic_package_from, pic_package_to)
            self.logger.debug(f"Computed BoW-orb distance : {bow_orb_dict}")
            merged_dict.update(bow_orb_dict)
        except AlgoFeatureNotPresentError as e:
            self.logger.warning(f"No feature present for bow-orbing algorithms.Normal if BOW-ORB is not activated in configuration. Error : {e}")

        self.logger.debug(f"Distance dict : {merged_dict}")
        return merged_dict

    # ==================== ------ INTER IMAGE DISTANCE ------- ====================
    def get_dist_and_decision_picture_to_picture(self, pic_package_from, pic_package_to) -> [float, scoring_datastrutures.DecisionTypes]:
        """
        Compare two pictures by their features, to return a one unique distance and a one unique decision. All activated algorithms are involved.
        :param pic_package_from: dict of one image features
        :param pic_package_to: dict of one image features
        :return: distance and a decision
        """
        # From distance between algos, obtain the distance between pictures
        merged_dict = self.get_dist_and_decision_algos_to_algos(pic_package_from, pic_package_to)

        try:
            dist = self.merging_engine.merge_algos_distance(merged_dict)
        except Exception as e:
            self.logger.critical(f"Error during merging of distances. Default distance taken : 1. Error: {e}")
            dist = 1

        try:
            decision = self.merging_engine.merge_algos_decision(merged_dict)
        except Exception as e:
            self.logger.critical(f"Error during merging of decisions. Default decision taken : MAYBE. Error: {e}")
            decision = scoring_datastrutures.DecisionTypes.MAYBE

        return dist, decision

    def match_enough(self, matching_picture: scoring_datastrutures.ImageMatch) -> bool:
        """
        Check if a match is good enough. Compare the distance between pictures with the threshold between clusters. Usable for storage graph.
        :param matching_picture: An ImageMatch object, which includes distance between pictures
        :return: boolean, True if pictures are close enough, False otherwise.
        """
        # Check if the matching pictures provided are "close enough" of the current picture.

        self.logger.critical(f" Max distance for new cluster in distance engine : {self.dist_conf.MAX_DIST_FOR_NEW_CLUSTER}")

        # Check if the picture is too far or not
        if matching_picture.distance <= self.dist_conf.MAX_DIST_FOR_NEW_CLUSTER:
            return True

        # TODO : Check for decisions
        if matching_picture.decision == dt.YES.name or matching_picture.decision == dt.MAYBE.name:
            return True

        # Picture is too "far"
        return False

    # ==================== ------ PICTURE TO CLUSTER DISTANCE ------- ====================

    def get_top_matching_clusters(self, cluster_list: List, image_dict: Dict) -> List[scoring_datastrutures.ClusterMatch]:
        """
        Evaluate the similarity between the given picture and each cluster's representative picture
        Returns a list of the N closest clusters
        :param cluster_list: The cluster list to iterate on, to check if the picture belongs to one of them
        :param image_dict: the picture features to use to check if belonging to each cluster
        :return: a top list of clusters with which the picture matches.
        """

        self.logger.debug(f"Finding top matching clusters for current picture in cluster list {cluster_list}")

        top_n_storage = scoring_datastrutures.TopN(self.dist_conf.TOP_N_CLUSTERS)

        # Evaluate similarity to each cluster
        for curr_cluster in cluster_list:
            self.logger.debug(f"Evaluating distance from current picture to cluster #{curr_cluster}")

            # Evaluate current distance to cluster
            tmp_dist, tmp_decision = self.get_distance_picture_to_cluster(curr_cluster, image_dict)

            # Store in datastructure
            tmp_cluster_match = scoring_datastrutures.ClusterMatch(cluster_id=curr_cluster,
                                                                   distance=tmp_dist,
                                                                   decision=tmp_decision)
            top_n_storage.add_element(tmp_cluster_match)

        # get top N clusters = Ask datastructure to return its top list
        return top_n_storage.get_top_n()

    def get_distance_picture_to_cluster(self, cluster_id: str, image_dict: Dict) -> [float, scoring_datastrutures.DecisionTypes]:
        """
        Go through N first picture of given cluster, and test their distance to given image
        Merge the results into one unified distance
        :param cluster_id: the cluster id of the cluster to compare
        :param image_dict: the image dict of the picture to compare
        :return: a distance and a decision, from picture to the cluster
        """

        self.logger.debug(f"Computing distance between cluster {cluster_id} and current picture")

        pict_to_test_per_cluster = self.dist_conf.PICT_TO_TEST_PER_CLUSTER

        list_dist_decision = []
        curr_picture_sorted_set = self.parent.db_utils.get_pictures_of_cluster(cluster_id)  # DECODE

        self.logger.debug(f"Retrieved pictures of cluster #{cluster_id} are {curr_picture_sorted_set}")

        for i, curr_picture in enumerate(curr_picture_sorted_set):
            if i < pict_to_test_per_cluster:
                self.logger.debug(f"Evaluating picture #{i} of current cluster")
                # We still have pictures to test for this cluster
                # Get picture dict
                curr_pic_dict = self.parent.get_dict_from_key(self.parent.storage_db_no_decode, curr_picture, pickle=True)

                # Evaluate distance between actual picture and cluster's pictures
                list_dist_decision.append(self.get_dist_and_decision_picture_to_picture(curr_pic_dict, image_dict))
            else:
                # We have tested the N first pictures of the cluster and so stop here
                break

        # Evaluation of the distance between pictures, and the decision
        dist_picture_to_cluster = self.merging_engine.merge_max_pictures_distance([i[0] for i in list_dist_decision])
        decision_picture_to_cluster = self.merging_engine.merge_pictures_decisions([i[1] for i in list_dist_decision])

        return dist_picture_to_cluster, decision_picture_to_cluster

    # ==================== ------ PICTURE TO ALL PICTURES DISTANCE ------- ====================

    def get_top_matching_pictures_from_clusters(self, cluster_list: List, image_dict: Dict) -> List[scoring_datastrutures.ImageMatch]:
        """
        Evaluate the similarity between the given picture and all pictures of cluster list.
        Returns a list of the N closest pictures and cluster, with distance
        :param cluster_list: The cluster list to iterate on, to check if the picture is near one of its picture
        :param image_dict: the picture features to use to check if near any pictures of the cluster list
        :return: List of Imagematch, undifferenciated of their origin cluster
        """

        self.logger.debug(f"Finding top matching pictures for current picture in all pictures of all clusters of the list={cluster_list}")

        top_n_storage = scoring_datastrutures.TopN(self.dist_conf.TOP_N_PICTURES)

        # For each cluster, iterate over all pictures of this cluster
        for curr_cluster in cluster_list:
            curr_picture_set = self.parent.db_utils.get_pictures_of_cluster(curr_cluster)

            for curr_picture in curr_picture_set:
                # Get picture dict
                curr_pic_dict = self.parent.get_dict_from_key(self.parent.storage_db_no_decode, curr_picture, pickle=True)

                # Evaluate distance between actual picture and cluster's pictures
                tmp_dist, tmp_decision = self.get_dist_and_decision_picture_to_picture(curr_pic_dict, image_dict)

                # Keep only N best picture = Store in datastructure
                tmp_image_match = scoring_datastrutures.ImageMatch(image_id=curr_picture, cluster_id=curr_cluster, distance=tmp_dist, decision=tmp_decision)
                top_n_storage.add_element(tmp_image_match)

        # get top N pictures
        return top_n_storage.get_top_n()

    # ==================== ------ PICTURE TO ALL PICTURES DISTANCE ------- ====================

    def get_best_n_pictures_of_cluster(self, cluster_id):
        # Get N best pictures of the given cluster
        # TODO : To complete with ZSET ...
        return
