#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==================== ------ STD LIBRARIES ------- ====================
import os
import sys
import uuid

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))

import carlhauser_server.Configuration.database_conf as database_conf
import carlhauser_server.Configuration.distance_engine_conf as distance_engine_conf

import carlhauser_server.DatabaseAccessor.database_worker as database_accessor


class Cluster_Engine(database_accessor.Database_Worker):
    def __init__(self, db_conf: database_conf, dist_conf: distance_engine_conf):
        super().__init__(db_conf)
        self.dist_conf = dist_conf

        self.CLUSTER_LIST = "cluster_list"

    # ==================== ------ SORTING AND SCORING ------- ====================

    def get_top_matching_clusters(self, image_dict: dict):
        # Evaluate the similarity between the given picture and each cluster's representative picture
        # Returns a list of the N closest clusters
        TOP_N_CLUSTERS = self.dist_conf.TOP_N_CLUSTERS
        PICT_TO_TEST_PER_CLUSTER = self.dist_conf.PICT_TO_TEST_PER_CLUSTER

        # Iterate over clusters
        cluster_list = self.get_cluster_list()

        # Evaluate each similiarity to each cluster
        for curr_cluster in cluster_list:
            # Evaluate current distance to cluster
            pass  # TODO : Evaluation of the distance between pictures
            # Store in datastructure
            # TODO : Create datastructure to handle X first elements ?

        # get top N clusters
        # TODO : Ask datastructure to return its top list

        # return list of [cluster_id, cluster_id ...]

    def get_top_matching_pictures_from_clusters(self, cluster_list: list, image_dict: dict):
        # Evaluate the similarity between the given picture and all pictures of cluster list.
        # Returns a list of the N closest pictures and cluster, with distance
        TOP_N_PICTURES = self.dist_conf.TOP_N_PICTURES  # TODO : 1 only ? We want to connect only to one picture the current picture ?

        # For each cluster, iterate over all picture of this cluster
        for curr_cluster in cluster_list:
            curr_picture_list = self.get_pictures_of_cluster(curr_cluster)

            for curr_picture in curr_picture_list:
                # Evaluate distance between actual picture and cluster's pictures
                pass  # TODO : Evaluation of the distance between pictures

                # Keep only N best picture = Store in datastructure
                # TODO : Create datastructure to handle X first elements ?
                # max(...,...)

        # get top N pictures
        # TODO : Ask datastructure to return its top list

        return  # top list [[picture, cluster], ...]

    def match_enough(self, top_matching_pictures):
        # Check if the matching pictures provided are "close enough" of the current picture.

        pass

    # ==================== ------ PICTURES LIST PER CLUSTER ------- ====================
    @staticmethod
    def get_setname_of_cluster(cluster_name):
        return '|'.join([cluster_name, 'pics'])

    ''' INVERTED LOOK-UP
    def get_cluster(self, image_id):
        # Get the cluster from which an image belongs to

        pass
    '''

    def get_pictures_of_cluster(self, cluster_name):
        # Get the list of pictures associated of the given cluster

        return self.storage_db.smembers(self.get_setname_of_cluster(cluster_name))

    # ==================== ------ CLUSTER LIST ------- ====================
    def get_cluster_list(self):
        # Get the list of pictures associated of the given cluster

        return self.storage_db.smembers(self.CLUSTER_LIST)

    def add_cluster(self, cluster_name):
        # Store a cluster's name in the list of cluster's names

        if self.storage_db.sismember(cluster_name) == 1:
            # The set does contains the cluster we want to add
            self.logger.error("A cluster is added to cluster list, but is already present. Collision in uuid or structural problem detected.")

        return self.storage_db.sadd(self.CLUSTER_LIST, cluster_name)

    def rem_cluster(self, cluster_name):
        # Remove a cluster's name of the list of cluster's names

        if self.storage_db.sismember(cluster_name) == 0:
            # The set does contains the cluster we want to add
            self.logger.error("A cluster is added to cluster list, but is already present. Structural problem detected.")

        return self.storage_db.srem(self.CLUSTER_LIST, cluster_name)

    # ==================== ------ ADDERS ------- ====================

    def add_picture_to_storage(self, id, image_dict: dict):
        # Store the dictionary of hashvalues in Redis under the given id

        return self.storage_db.hmset(name=id, mapping=image_dict)

    def add_picture_to_cluster(self, image_id, cluster_id):
        # Add a picture to a cluster

        set_name = self.get_setname_of_cluster(cluster_id)

        if self.storage_db.scard(set_name) == 0:
            # The set does not exist, and so the cluster
            self.logger.error("A picture is added to a cluster that does not exists. Please review structural behavior.")

        # Add the picture to the set
        success = self.storage_db.sadd(set_name, image_id)
        self.logger.info(f"Added picture {image_id} to {cluster_id} cluster under set name {set_name}")

        return success

    def add_picture_to_new_cluster(self, image_id):
        # Add picture to a freshly created cluster

        # Generate random id
        cluster_name = str(uuid.uuid4())
        set_name = self.get_setname_of_cluster(cluster_name)

        # Add cluster to cluster list
        self.add_cluster(cluster_name)

        # Add the picture to the set
        self.storage_db.sadd(set_name, image_id)
        self.logger.info(f"Added picture {image_id} to NEW {cluster_name} cluster under set name {set_name}")

        return cluster_name

    # ==================== ------ BACKGROUND COMPUTATION ------- ====================
    def add_to_review(self, image_id):
        # Add the picture to be reviewed in few time (100_queue, 1000_queue, ...)

        pass

    def reevaluate_representative_picture_order(self, cluster_id, fetched_id=None):
        # Re-evaluate the representative picture.
        # 0(N²) operation with N being the number of elements in the cluster

        if fetched_id is None:
            # We don't know which picture was the last one added. Perform full re-evaluation
            pass
        else:
            # We know which picture was added last, and so begin by this one.
            pass

        # evaluate
        # TODO : Somewhat already done before. May be able to memoize the computed values ?
        pass
