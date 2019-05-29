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

    # ==================== Export / Import ====================

    def export_as_dict(self):
        tmp_dict = {}
        tmp_dict["meta"] = self.meta.export_as_dict()
        tmp_dict["clusters"] = [cluster.export_as_dict() for cluster in self.clusters.values()]
        tmp_dict["nodes"] = [node.export_as_dict() for node in self.nodes.values()]
        tmp_dict["edges"] = [edge.export_as_dict() for edge in self.edges]

        return tmp_dict

    @staticmethod
    def load_from_dict(input):
        meta = metadata.Metadata.load_from_dict(input["meta"])
        tmp_graph = GraphDataStruct(meta)

        tmp_clusters = [cluster.Cluster.load_from_dict(cluster_dict) for cluster_dict in input["clusters"]]
        tmp_nodes = [node.Node.load_from_dict(node_dict) for node_dict in input["nodes"]]
        tmp_edges = [edge.Edge.load_from_dict(edge_dict) for edge_dict in input["edges"]]

        for c in tmp_clusters :
            tmp_graph.add_cluster(c)

        for n in tmp_nodes :
            tmp_graph.add_node(n)

        for e in tmp_edges :
            tmp_graph.add_edge(e)

        return tmp_graph


