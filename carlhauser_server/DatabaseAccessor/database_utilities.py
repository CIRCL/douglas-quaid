#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
# ==================== ------ STD LIBRARIES ------- ====================
import os
import pathlib
import sys
import uuid
from typing import List

import redis

# ==================== ------ PERSONAL LIBRARIES ------- ====================
from common.Graph.cluster import Cluster
from common.Graph.edge import Edge
from common.Graph.graph_datastructure import GraphDataStruct
from common.Graph.metadata import Metadata, Source
from common.Graph.node import Node

sys.path.append(os.path.abspath(os.path.pardir))


class DBUtilities:
    def __init__(self, db_access_decode: redis.client.Redis, db_access_no_decode: redis.client.Redis):
        self.logger = logging.getLogger(__name__)
        self.db_access_decode = db_access_decode
        self.db_access_no_decode = db_access_no_decode
        self.CLUSTER_LIST = "cluster_list"

    # ==================== ------ CLUSTER LIST ------- ====================
    def get_cluster_list(self) -> List:
        """
        # Get the list of pictures associated with a given cluster
        :return: List of cluster id #TODO : CHECK = Specify type
        """

        return self.db_access_decode.smembers(self.CLUSTER_LIST)

    def add_cluster(self, cluster_name: str) -> bool:
        """
        Store a cluster's name in the list of cluster's names
        :param cluster_name: The name of the cluster to add
        :return: boolean, True if successfully added, False otherwise
        """

        if self.db_access_decode.sismember(self.CLUSTER_LIST, cluster_name) == 1:
            # The set does contains the cluster we want to add
            self.logger.error("A cluster is added to cluster list, but is already present. Collision in uuid or structural problem detected.")

        return self.db_access_decode.sadd(self.CLUSTER_LIST, cluster_name)

    def rem_cluster(self, cluster_name: str) -> bool:
        """
        Remove a cluster's name of the list of cluster's names
        :param cluster_name: The name of the cluster to remove
        :return: boolean, True if successfully removed, False otherwise
        """

        if self.db_access_decode.sismember(self.CLUSTER_LIST, cluster_name) == 0:
            # The set does contains the cluster we want to add
            self.logger.error("A cluster is removed to cluster list, but is already non existent. Structural problem detected.")

        return self.db_access_decode.srem(self.CLUSTER_LIST, cluster_name)

    # ==================== ------ ADDERS ------- ====================

    def add_picture_to_cluster(self, image_id: str, cluster_id: str, score: int = 100) -> bool:
        """
        Add a picture to a cluster (already existing)
        :param image_id: id of the picture to add
        :param cluster_id: id of the cluster to which the picture will be added
        :param score: score of the picture (clusters are sorted set ! So how high the picture will be stored ?)
        :return: boolean, True if successfully added, False otherwise
        """

        set_name = self.get_setname_of_cluster(cluster_id)

        if self.db_access_decode.zcard(set_name) == 0:
            # The set does not exist, and so the cluster
            self.logger.error("A picture is added to a cluster that does not exists. Please review structural behavior.")

        # Add the picture to the set
        success = self.db_access_decode.zadd(set_name, {image_id: score})  # SORTED SET
        self.logger.info(f"Added picture {image_id} to {cluster_id} cluster under set name {set_name}")

        return success

    def add_picture_to_new_cluster(self, image_id: str, score: float = 100) -> str:
        """
        Add a picture to a cluster (freshly created)
        :param image_id: id of the picture to add
        :param score: score of the picture (clusters are sorted set ! So how high the picture will be stored ?)
        :return: id of the created cluster for this picture
        """

        # Generate random id
        cluster_id = self.get_new_cluster_id()
        set_name = self.get_setname_of_cluster(cluster_id)

        # Add cluster to cluster list
        self.add_cluster(cluster_id)

        # Add the picture to the set
        self.db_access_decode.zadd(set_name, {image_id: score})  # SORTED SET
        self.logger.info(f"Added picture {image_id} to NEW {cluster_id} cluster under set name {set_name}")

        return cluster_id

    def update_picture_score_of_cluster(self, cluster_id: str, image_id: str, new_score: float) -> bool:
        """
        Update the set "ranking" value of a picture into a cluster
        :param cluster_id: id of the cluster to which the picture belongs
        :param image_id: id of the picture to add
        :param new_score: new score of the picture
        :return: True if success, Exception if unsuccessful
        """

        set_name = self.get_setname_of_cluster(cluster_id)
        self.db_access_decode.zadd(set_name, {image_id: new_score}, xx=True)

        return True

    @staticmethod
    def get_new_cluster_id() -> str:
        """
        Generate cluster id
        :return: a new cluster id to use
        """
        return '|'.join(["cluster", str(uuid.uuid4())])

    # ==================== ------ PICTURES LIST PER CLUSTER ------- ====================

    def get_pictures_of_cluster(self, cluster_name: str, with_score=False) -> set:
        """
        Retrieve the set of pictures ids from a cluster
        :param cluster_name: the cluster id from which to dump pictures
        :param with_score: boolean to specify if scores of pictures should also be dumped
        :return: the set of pictures (with or without scores)
        """
        self.logger.debug(f"Retrieving picture list of cluster {cluster_name}")

        if type(cluster_name) is not str:
            raise Exception("Invalid cluster name, not a string.")

        # Get the list of pictures associated of the given cluster
        return self.db_access_decode.zrange(self.get_setname_of_cluster(cluster_name), 0, -1, withscores=with_score)  # SORTED SET

    @staticmethod
    def get_setname_of_cluster(cluster_name: str) -> str:
        """
        Generate the key of the set of pictures
        :param cluster_name: the cluster name to which we want to generate the set of pictures key
        :return: the set of picture key
        """
        return '|'.join([cluster_name, 'pics'])

    # ==================== ------ BACKGROUND COMPUTATION ------- ====================

    def add_to_review(self, image_id):
        """
        Add the picture to be reviewed in few time (100_queue, 1000_queue, ...)
        TODO ! !
        :param image_id:
        :return:
        """

        # TODO
        return

    # ==================== ------ EXPORTATION ------- ====================

    def get_storage_graph(self) -> GraphDataStruct:
        """
        # TODO : Move to API ?
        Export the current state of the database as a graph datastructure. This represents the storage graph of the server.
        :return: The storage graph of the server, as is in the database
        """

        # Create a graphe structure
        tmp_meta = Metadata(Source.DBDUMP)
        tmp_graph = GraphDataStruct(tmp_meta)

        # Get all clusters
        cluster_list = self.get_cluster_list()

        # For each cluster, fetch all pictures and store it
        for cluster_id in cluster_list:
            tmp_graph.add_cluster(Cluster(label="", id=cluster_id, image=""))

            picture_list = self.get_pictures_of_cluster(cluster_id, with_score=True)
            self.logger.info(f"Picture list : {picture_list}")

            for picture in picture_list:
                # Label = picture score, here
                tmp_graph.add_node(Node(label=picture[1], id=picture[0], image=""))
                tmp_graph.add_edge(Edge(_from=cluster_id, _to=picture[0]))

        return tmp_graph

    def export_pictures_bmp(self, path_to_save: pathlib.Path):

        # TODO

        return
