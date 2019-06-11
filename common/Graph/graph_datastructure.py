#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==================== ------ STD LIBRARIES ------- ====================
from typing import List, Dict
from enum import Enum, auto
import logging
import sys, os
import pprint

# ==================== ------ PERSONAL LIBRARIES ------- ====================

sys.path.append(os.path.abspath(os.path.pardir))
FORMATTER = logging.Formatter('%(asctime)s - + %(relativeCreated)d - %(name)s - %(levelname)s - %(message)s')

from common.Graph import cluster, edge, metadata, node


class GraphDataStruct:
    # Handle the complete graph

    def __init__(self, meta: metadata.Metadata):
        self.logger = logging.getLogger(__name__)

        self.meta = meta

        self.clusters = {}
        self.edges = []
        self.nodes = {}

    # ==================== Adding elements to the graph ====================

    def add_node(self, node: node.Node):
        # Add a node to the graph (a picture, not a cluster)
        self.nodes[node.id] = node

    def add_cluster(self, cluster: cluster.Cluster):
        # Add a cluster to the graph (not a picture)
        self.clusters[cluster.id] = cluster

    def add_edge(self, edge: edge.Edge):
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

    def add_cluster_of_nodes(self, cluster: cluster.Cluster, nodes: List[node.Node], color="gray"):
        # Add a cluster to the graph
        self.clusters[cluster.id] = cluster

        # For each node, add the node and add an edge between the cluster and the node
        for n in nodes:
            self.nodes[n.id] = n
            self.edges.append(edge.Edge(cluster.id, n.id, color))

    # ==================== Conversion ====================

    def replace_id_from_mapping(self, filename_to_id):
        mapping_old_id_new_id = {}

        # For all nodes
        for n in self.nodes.values():
            tmp_old_id = n.id
            # Modify the name if presents in the provided mapping, or keep original id
            n.id = filename_to_id.get(n.image, n.id)
            # Store the modification in a mapping
            mapping_old_id_new_id[tmp_old_id] = n.id

        # For all clusters and egdes updates ids
        for c in self.clusters.values():
            for old, new in mapping_old_id_new_id.items():
                c.update_member_id(old, new)

        for e in self.edges:
            for old, new in mapping_old_id_new_id.items():
                e.update_member_id(old, new)

        self.logger.warning("Be aware that performing an ID mapping can leads to node fusion : some nodes can be mapped to the same id, and so, some nodes can be lost.")
        # Create new node dict, with new ids
        tmp_dict = {n.id: n for n in self.nodes.values()}
        self.nodes = tmp_dict

        # Create new cluster dict, with new ids
        tmp_dict = {c.id: c for c in self.clusters.values()}
        self.clusters = tmp_dict

        return mapping_old_id_new_id

    def get_clusters(self):
        return list(self.clusters.values())

    def get_edges_dict(self):
        # Returns a list of edges as a dict, node_id => cluster_id
        tmp_dict = {}

        for edge in self.edges:
            if edge._from in self.clusters.keys():  # "From" is a cluster
                tmp_dict[edge._to] = edge._from
            elif edge._to in self.clusters.keys():  # "To" is a cluster
                tmp_dict[edge._from] = edge._to
            else:  # Edge between two nodes ?
                raise Exception("Edges between nodes without cluster are not handled (for now).")

        return tmp_dict

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

        for c in tmp_clusters:
            tmp_graph.add_cluster(c)

        for n in tmp_nodes:
            tmp_graph.add_node(n)

        for e in tmp_edges:
            tmp_graph.add_edge(e)

        return tmp_graph


def merge_graphs(visjs_graph: GraphDataStruct, db_graph: GraphDataStruct, cluster_mapping : List[List[cluster.Cluster]]) -> Dict:
    # Merge a visjs and db graph to produce only one visjs graph, with colors depending on good/bad matches

    tmp_dict = {}

    # Merge metas
    tmp_dict["meta_1"] = visjs_graph.meta.export_as_dict()
    tmp_dict["meta_2"] = db_graph.meta.export_as_dict()

    # No need to merge nodes or clusters, we keep ones from graph one
    tmp_dict["clusters"] = [cluster.export_as_dict() for cluster in visjs_graph.clusters.values()]
    tmp_dict["nodes"] = [node.export_as_dict() for node in visjs_graph.nodes.values()]

    # Construct cluster mapping db_id => vis_id
    # DEBUG pprint.pprint(cluster_mapping)
    mapping = {cluster_pair[1].id: cluster_pair[0].id for cluster_pair in cluster_mapping}

    # Create dict node_id => cluster_id for vis graph and db graph
    vis_edges = visjs_graph.get_edges_dict()
    db_edges = db_graph.get_edges_dict()

    # Convert db cluster id to visjs cluster id
    db_edges = {edge_from: mapping.get(edge_to, "ERROR") for edge_from, edge_to in db_edges.items()}

    new_edges_list = merge_edges_with_colors(vis_edges, db_edges)

    tmp_dict["edges"] = [edge.export_as_dict() for edge in new_edges_list]

    return tmp_dict


def merge_edges_with_colors(vis_edges: Dict, db_edges: Dict) -> List[edge.Edge]:
    # Merge edges dictionnary
    edge_list = []

    # Iterate over visjs edges
    for v_edge_from, v_edge_to in vis_edges.items():
        # If edge is present in db and with same "to", put green
        if v_edge_from in db_edges and v_edge_to == db_edges[v_edge_from]:
            edge_list.append(edge.Edge(v_edge_from, v_edge_to, {"color":"green"}))

        # If edge is present in db, but not with same "to", put red
        elif v_edge_from in db_edges and v_edge_to != db_edges[v_edge_from]:
            edge_list.append(edge.Edge(v_edge_from, v_edge_to, {"color":"orange"}))
            edge_list.append(edge.Edge(v_edge_from, db_edges[v_edge_from], {"color":"red"}))

        # If edge is not present in db, problem = put black
        else:  # v_edge_from not in db_edges :
            edge_list.append(edge.Edge(v_edge_from, v_edge_to, {"color":"black"}))

    return edge_list
