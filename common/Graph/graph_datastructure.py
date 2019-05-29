#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==================== ------ STD LIBRARIES ------- ====================
from typing import List, Dict
from enum import Enum, auto
import logging
import sys, os

# ==================== ------ PERSONAL LIBRARIES ------- ====================

sys.path.append(os.path.abspath(os.path.pardir))
FORMATTER = logging.Formatter('%(asctime)s - + %(relativeCreated)d - %(name)s - %(levelname)s - %(message)s')

from common.Graph import cluster, edge, metadata, node


class GraphDataStruct:
    # Handle the complete graph

    def __init__(self, meta: metadata.Metadata):
        self.meta = meta

        self.clusters = {}
        self.edges = []
        self.nodes = {}

    # ==================== Adding elements to the graph ====================

    def add_node(self, node:node.Node):
        # Add a node to the graph (a picture, not a cluster)
        self.nodes[node.id] = node

    def add_cluster(self, cluster:cluster.Cluster):
        # Add a cluster to the graph (not a picture)
        self.clusters[cluster.id] = cluster

    def add_edge(self, edge:edge.Edge):
        # Add an edge to the graph
        self.edges.append(edge)
        if edge._from in self.clusters.keys():
            self.clusters[edge._from].add_member_id(edge._to)

    '''
    def rem_edge(self, edge:edge.Edge):
        # Add an edge to the graph
        self.edges.remove(edge)
        if edge._from in self.clusters.keys():
            self.clusters[edge._from].remove_member_id(edge._to)
    '''

    def add_cluster_of_nodes(self, cluster:cluster.Cluster, nodes:List[node.Node], color="gray"):
        # Add a cluster to the graph
        self.clusters[cluster.id] = cluster

        # For each node, add the node and add an edge between the cluster and the node
        for n in nodes :
            self.nodes[n.id] = n
            self.edges.append(edge.Edge(cluster.id,n.id, color))

    # ==================== Export ====================


    '''
        "nodes": [
            {
                "id": 0,
                "shape": "image",
                "image": "musk.fyi.bmp"
            },
        (...)
        edges : [
            {
            "from": 49,
            "to": 41,
            "label": "rank 0 (0.0)",
            "value": "20.0",
            "title": 0.0
        },
    '''

    def export_as_json(self):
        json = {}
        json["meta"] = self.meta.export_as_json()
        json["clusters"] = [cluster.export_as_json() for cluster in self.clusters.values()]
        json["nodes"] = [node.export_as_json() for node in self.nodes.values()]
        json["edges"] = [edge.export_as_json() for edge in self.edges]

        return json

