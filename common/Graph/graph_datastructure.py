#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import pathlib
from typing import List, Dict

import common.ImportExport.json_import_export as json_import_export
from common.Graph import cluster, edge, metadata, node
from common.PerformanceDatastructs.clustermatch_datastruct import ClusterMatch
from common.environment_variable import load_server_logging_conf_file

load_server_logging_conf_file()


class GraphDataStruct:
    """
    Handle the complete graph
    """

    def __init__(self, meta: metadata.Metadata):
        self.logger = logging.getLogger(__name__)

        self.meta = meta

        self.clusters: Dict[str, cluster.Cluster] = {}
        self.edges: List[edge.Edge] = []
        self.nodes: Dict[str, node.Node] = {}

    # ==================== Adding elements to the graph ====================

    def add_node(self, node: node.Node):
        """
        Add a node to the graph (a picture, not a cluster)
        :param node: Node to add to the graph
        :return: Nothing
        """
        self.nodes[node.id] = node

    def add_cluster(self, cluster: cluster.Cluster):
        """
        Add a cluster to the graph (not a picture)
        :param cluster: Cluster to add to the graph
        :return: Nothing
        """
        self.clusters[cluster.id] = cluster

    def add_cluster_with_nodes(self, cluster: cluster.Cluster, nodes: List[node.Node], color="gray"):
        """
        Add a cluster to the graph with its nodes
        :param cluster: Cluster to add to the graph
        :param nodes: List of nodes to add to the graph and to link to the cluster
        :param color: Color of the links between this cluster and these nodes
        :return: Nothing
        """

        self.clusters[cluster.id] = cluster

        # For each node, add the node and add an edge between the cluster and the node
        for n in nodes:
            self.nodes[n.id] = n
            self.edges.append(edge.Edge(cluster.id, n.id, color))

    def add_edge(self, edge: edge.Edge):
        """
        Add an edge to the graph
        :param edge: Edge to add to the graph
        :return: Nothing
        """

        self.edges.append(edge)
        if edge._from in self.clusters.keys():
            self.clusters[edge._from].add_member_id(edge._to)
        if edge._to in self.clusters.keys():
            self.clusters[edge._to].add_member_id(edge._from)

    '''
    def rem_edge(self, edge:edge.Edge):
        # Remove an edge to the graph
        self.edges.remove(edge)
        if edge._from in self.clusters.keys():
            self.clusters[edge._from].remove_member_id(edge._to)
    '''

    # ==================== Request ====================

    def are_ids_in_same_cluster(self, id_1, id_2):
        """
        Return True if both nodes ids are in this cluster (by ids) # TODO : make test !
        :param id_1: first id
        :param id_2: second id
        :return: True if both ids are in the same cluster, false otherwise
        """

        are_in_same = False
        for c in self.clusters.values():
            if c.are_in_same_cluster(id_1, id_2):
                return True

        return are_in_same

    def are_names_in_same_cluster(self, name_1: str, name_2: str) -> bool:
        """
        Return True if both nodes id are in this cluster (by name).
        Translate names to id and fallback to check if ids in same cluster # TODO : make test !
        :param name_1: first name
        :param name_2: second name
        :return: True if both names are in the same cluster, false otherwise
        """

        one_found = False
        id_1 = None
        id_2 = None

        # For each node
        for n in self.nodes.values():
            if n.image == name_1:
                id_1 = n.id
                if not one_found:  # First id found = Continue
                    one_found = True
                elif one_found:
                    break  # Second id found ! = Stop
            if n.image == name_2:
                id_2 = n.id
                if not one_found:  # First id found = Continue
                    one_found = True
                elif one_found:
                    break  # Second id found ! = Stop

        if id_1 is None or id_2 is None:
            raise Exception(f"Image Name not found in graph structure ! {name_1} => {id_1} or {name_2} =>{id_2}")

        return self.are_ids_in_same_cluster(id_1, id_2)

    # ==================== Conversion ====================

    def replace_id_from_mapping(self, filename_to_id: Dict) -> Dict:
        """
        Replace olds id by new ids, if provided in the input list (filename_to_id).
        Ex : {"toto":id=2} input with {Edge : {"toto":id=1}} input => {Edge : {"toto":id=2}} output
        :param filename_to_id: a mapping from name to ids
        :return: a mapping from old id to new ids (Ex : {2:1} in previus example) + change state of the graph
        """

        mapping_old_id_new_id = {}

        # For all nodes, transform the input mapping into a dict
        for n in self.nodes.values():
            tmp_old_id = n.id
            # Modify the name if presents in the provided mapping, or keep original id
            n.id = filename_to_id.get(n.image, n.id)
            # Store the modification in a mapping
            mapping_old_id_new_id[tmp_old_id] = n.id

        # For all clusters updates ids
        for c in self.clusters.values():
            for old, new in mapping_old_id_new_id.items():
                c.update_member_id(old, new)

        # For all edges updates ids
        for e in self.edges:
            for old, new in mapping_old_id_new_id.items():
                e.update_member_id(old, new)

        self.logger.warning("Be aware that performing an ID mapping can leads to node fusion : some nodes can be mapped to the same id, and so, some nodes can be lost.")

        # Reconstruct node dict, with new ids
        tmp_dict = {n.id: n for n in self.nodes.values()}
        self.nodes = tmp_dict

        # Reconstruct cluster dict, with new ids
        tmp_dict = {c.id: c for c in self.clusters.values()}
        self.clusters = tmp_dict

        return mapping_old_id_new_id

    def get_clusters(self) -> List[cluster.Cluster]:
        """
        Get the list of cluster
        :return: List of clusters of the graph
        """
        return list(self.clusters.values())

    def get_edges_dict(self) -> Dict[str, str]:
        """
        Returns a list of edges as a dict in the order (node_id => has edge to => cluster_id)
        :return:
        """

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

    def copy_ids_to_image(self):
        """
        Copy "id" values of nodes to their "image" field
        (useful if we have no image, and id are actual path)
        :return: Nothing (+ change the internal state)
        """
        for tmp_node in self.nodes.values():
            tmp_node.copy_ids_to_image()

    def export_as_dict(self) -> Dict:
        """
        Export the current graph as a dict
        :return: A dict version of the graph
        """

        tmp_dict = {}
        tmp_dict["meta"] = self.meta.export_as_dict()
        tmp_dict["clusters"] = [cluster.export_as_dict() for cluster in self.clusters.values()]
        tmp_dict["nodes"] = [node.export_as_dict() for node in self.nodes.values()]
        tmp_dict["edges"] = [edge.export_as_dict() for edge in self.edges]

        return tmp_dict

    @staticmethod
    def load_from_dict(tmp_input: Dict):
        """
        Load/ Import a graph from a dict
        :param tmp_input: A Dict version of the graph to import
        :return: The graph as an object
        """

        meta = metadata.Metadata.load_from_dict(tmp_input["meta"])
        tmp_graph = GraphDataStruct(meta)

        tmp_clusters = [cluster.Cluster.load_from_dict(cluster_dict) for cluster_dict in tmp_input["clusters"]]
        tmp_nodes = [node.Node.load_from_dict(node_dict) for node_dict in tmp_input["nodes"]]
        tmp_edges = [edge.Edge.load_from_dict(edge_dict) for edge_dict in tmp_input["edges"]]

        for c in tmp_clusters:
            tmp_graph.add_cluster(c)

        for n in tmp_nodes:
            tmp_graph.add_node(n)

        for e in tmp_edges:
            tmp_graph.add_edge(e)

        return tmp_graph


def merge_graphs(visjs_graph: GraphDataStruct, db_graph: GraphDataStruct, cluster_mapping: List[ClusterMatch]) -> Dict:
    '''
    Merge two graphs into one unique graph. Uses the list of clusters matches to merge each cluster with each other.
    Merge a visjs and db graph to produce only one visjs graph, with colors depending on good/bad matches
    :param visjs_graph: The first graph to merge (ground truth one)
    :param db_graph: The second graph to merge (extracted from server)
    :param cluster_mapping: The list of clusterMatch that say "This cluster is the same as this one" for the merge.
    :return: A datastructure (json style/ dict style) that displays all data
    '''

    tmp_dict = {}

    # Merge metas
    tmp_dict["meta_1"] = visjs_graph.meta.export_as_dict()
    tmp_dict["meta_2"] = db_graph.meta.export_as_dict()

    # No need to merge nodes or clusters, we keep ones from graph one
    tmp_dict["clusters"] = [c.export_as_dict() for c in visjs_graph.clusters.values()]
    tmp_dict["nodes"] = [n.export_as_dict() for n in visjs_graph.nodes.values()]

    # Construct cluster mapping db_id => vis_id
    # DEBUG pprint.pprint(cluster_mapping)
    mapping = {cluster_pair.cluster_2.id: cluster_pair.cluster_1.id for cluster_pair in cluster_mapping}

    # Create dict node_id => cluster_id for vis graph and db graph
    vis_edges = visjs_graph.get_edges_dict()
    db_edges = db_graph.get_edges_dict()

    # Convert db cluster id to visjs cluster id
    db_edges = {edge_from: mapping.get(edge_to, "ERROR") for edge_from, edge_to in db_edges.items()}

    new_edges_list = merge_edges_with_colors(vis_edges, db_edges)

    tmp_dict["edges"] = [e.export_as_dict() for e in new_edges_list]

    return tmp_dict


def merge_edges_with_colors(vis_edges: Dict, db_edges: Dict) -> List[edge.Edge]:
    """
    Merge a edges of two graphs with colors depending on good/bad matches
    :param vis_edges: The first edges set to merge (ground truth one)
    :param db_edges: The second edges set to merge (extracted from server)
    :return: A list of edges with colors
    """
    # Merge edges dictionnary
    edge_list = []

    # Iterate over visjs edges
    for v_edge_from, v_edge_to in vis_edges.items():
        # If edge is present in db and with same "to", put green
        if v_edge_from in db_edges and v_edge_to == db_edges[v_edge_from]:
            edge_list.append(edge.Edge(v_edge_from, v_edge_to, {"color": "green"}))

        # If edge is present in db, but not with same "to", put red
        elif v_edge_from in db_edges and v_edge_to != db_edges[v_edge_from]:
            edge_list.append(edge.Edge(v_edge_from, v_edge_to, {"color": "orange"}))
            edge_list.append(edge.Edge(v_edge_from, db_edges[v_edge_from], {"color": "red"}))

        # If edge is not present in db, problem = put black
        else:  # v_edge_from not in db_edges :
            edge_list.append(edge.Edge(v_edge_from, v_edge_to, {"color": "black"}))

    return edge_list


def load_visjs_to_graph(visjs_json_path: pathlib.Path = None) -> GraphDataStruct:
    """
    Load VisJS to graph datastructure
    :param visjs_json_path: path to the visjs graph storage
    :return: The graph datastructure as an object
    """
    if visjs_json_path is None:
        raise Exception("VisJS ground truth path not set. Impossible to evaluate.")
    else:
        # 1. Load pictures to visjs = node server.js -i ./../douglas-quaid/datasets/MINI_DATASET/ -t ./TMP -o ./TMP
        # 2. Cluster manually pictures in visjs = < Do manual stuff>
        # 3. Load json graphe
        visjs = json_import_export.load_json(visjs_json_path)
        visjs = GraphDataStruct.load_from_dict(visjs)

        return visjs
