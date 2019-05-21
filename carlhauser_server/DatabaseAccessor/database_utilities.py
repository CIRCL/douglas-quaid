#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
# ==================== ------ STD LIBRARIES ------- ====================
import os
import pathlib
import sys
import time

import redis
import uuid
import redis
import logging

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))


class DBUtilities():
    def __init__(self, db_access_decode: redis.client.Redis, db_access_no_decode: redis.client.Redis):
        self.logger = logging.getLogger(__name__)
        self.db_access_decode = db_access_decode
        self.db_access_no_decode = db_access_no_decode
        self.CLUSTER_LIST = "cluster_list"

    # ==================== ------ CLUSTER LIST ------- ====================
    def get_cluster_list(self):
        # Get the list of pictures associated of the given cluster
        return self.db_access_decode.smembers(self.CLUSTER_LIST)

    def add_cluster(self, cluster_name):
        # Store a cluster's name in the list of cluster's names
        if self.db_access_decode.sismember(self.CLUSTER_LIST, cluster_name) == 1:
            # The set does contains the cluster we want to add
            self.logger.error("A cluster is added to cluster list, but is already present. Collision in uuid or structural problem detected.")

        return self.db_access_decode.sadd(self.CLUSTER_LIST, cluster_name)

    def rem_cluster(self, cluster_name):
        # Remove a cluster's name of the list of cluster's names
        if self.db_access_decode.sismember(self.CLUSTER_LIST, cluster_name) == 0:
            # The set does contains the cluster we want to add
            self.logger.error("A cluster is added to cluster list, but is already present. Structural problem detected.")

        return self.db_access_decode.srem(self.CLUSTER_LIST, cluster_name)

    # ==================== ------ ADDERS ------- ====================

    def add_picture_to_cluster(self, image_id, cluster_id):
        # Add a picture to a cluster

        set_name = self.get_setname_of_cluster(cluster_id)

        if self.db_access_decode.scard(set_name) == 0:
            # The set does not exist, and so the cluster
            self.logger.error("A picture is added to a cluster that does not exists. Please review structural behavior.")

        # Add the picture to the set
        # success = self.db_access_decode.sadd(set_name, image_id) # SET
        success = self.db_access_decode.zadd(set_name, {image_id:2}) # SORTED SET
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
        # self.db_access_decode.sadd(set_name, image_id) # SET
        self.db_access_decode.zadd(set_name, {image_id:2}) # SORTED SET 2 = DEFAULT VALUE
        self.logger.info(f"Added picture {image_id} to NEW {cluster_name} cluster under set name {set_name}")

        return cluster_name

    # ==================== ------ PICTURES LIST PER CLUSTER ------- ====================

    def get_pictures_of_cluster(self, cluster_name) -> set:
        self.logger.debug(f"Retrieving picture list of cluster {cluster_name}")

        if type(cluster_name) is not str :
            raise Exception("Invalid cluster name, not a string.")

        # Get the list of pictures associated of the given cluster
        # return self.db_access_decode.smembers(self.get_setname_of_cluster(cluster_name)) # SET
        return self.db_access_decode.zrange(self.get_setname_of_cluster(cluster_name),0,-1) # SORTED SET

    @staticmethod
    def get_setname_of_cluster(cluster_name):
        return '|'.join([cluster_name, 'pics'])

        # ==================== ------ BACKGROUND COMPUTATION ------- ====================

    def add_to_review(self, image_id):
        # Add the picture to be reviewed in few time (100_queue, 1000_queue, ...)
        #TODO
        return

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
        return
