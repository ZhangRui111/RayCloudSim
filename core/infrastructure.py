import networkx as nx
from typing import Optional, Dict, List

from core.link import Link
from core.node import Node

__all__ = ["Infrastructure"]


class Infrastructure(object):
    """Class representing the infrastructure network with nodes and links.

    This class uses a NetworkX MultiDiGraph to model the network, allowing for
    multiple links between the same pair of nodes.

    This class provides methods to manage the infrastructure graph by adding/removing
    nodes and links, as well as retrieving paths, nodes, and links with various
    attributes.
    """

    def __init__(self):
        """Initializes the infrastructure with an empty directed graph."""
        self.graph = nx.MultiDiGraph()

    def add_node(self, node: Node):
        """Add a node to the infrastructure graph.

        If a node with the same name does not already exist, it will be added
        to the graph. If the node has location information, it is stored as
        a 'pos' attribute for potential visualization.

        Args:
            node: The Node object to add.
        """
        if node.name not in self.graph:
            node_data = {'data': node}
            if node.location:
                node_data['pos'] = list(node.location.loc())
            self.graph.add_node(node.name, **node_data)

    def remove_node(self, name: str):
        """Remove a node and all its adjacent edges from the infrastructure by node name.

        Args:
            name: The name of the node to remove.
        """
        if name in self.graph:
            self.graph.remove_node(name)

    def add_link(self, link: Link, key=None):
        """Add a link between two nodes in the infrastructure graph.

        If the source or destination nodes of the link do not exist in the graph,
        they will be added automatically. Link attributes like distance and latency
        are stored as edge data for use in pathfinding algorithms.

        Args:
            link: The Link object to add.
            key: An optional hashable identifier to distinguish multi-edges
                 between the same pair of nodes. Defaults to the lowest unused integer.
        """
        self.add_node(link.src)
        self.add_node(link.dst)
        # the keyword [dis/latency/*other] is for the weight in
        # get_shortest_path/links
        self.graph.add_edge(link.src.name, link.dst.name, key=key, data=link,
                            dis=link.dis, latency=link.base_latency)

    def remove_link(self, src_name: str, dst_name: str, key=None):
        """Remove a specific link between two nodes identified by their names.

        Args:
            src_name: The name of the source node of the link.
            dst_name: The name of the destination node of the link.
            key: The hashable identifier for the specific link (required for multi-edges).
                 Defaults to None, which may remove an arbitrary edge if multiple exist.

        Raises:
            networkx.exception.NetworkXError: If the specified link does not exist.
        """
        self.graph.remove_edge(src_name, dst_name, key=key)

    def get_node(self, name: str) -> Node:
        """Retrieve a specific node by its name.

        Args:
            name: The name of the node to retrieve.

        Returns:
            The Node object corresponding to the given name.

        Raises:
            KeyError: If a node with the given name does not exist.
        """
        return self.graph.nodes[name]["data"]

    def get_link(self, src_name: str, dst_name: str, key=0) -> Link:
        """Retrieve a specific link by the source and destination node names and optional key.

        Args:
            src_name: The name of the source node.
            dst_name: The name of the destination node.
            key: The key identifying the specific link (for multi-edges). Defaults to 0.

        Returns:
            The Link object corresponding to the specified edge.

        Raises:
            KeyError: If the specified link does not exist.
        """
        return self.graph.edges[src_name, dst_name, key]["data"]

    def get_nodes(self) -> Dict[str, Node]:
        """Retrieve all nodes in the infrastructure.

        Returns:
            A dictionary where keys are node names and values are Node objects.
        """
        return dict(nx.get_node_attributes(self.graph, 'data'))

    def get_links(self) -> Dict[tuple, Link]:
        """Retrieve all links in the infrastructure.

        Returns:
            A dictionary where keys are tuples representing edges ((src_name, dst_name, key))
            and values are Link objects.
        """
        return nx.get_edge_attributes(self.graph, 'data')

    def get_shortest_path(self, src_name: str, dst_name: str, weight=None) -> List[str]:
        """Retrieve the shortest path (sequence of node names) between two nodes.

        Args:
            src_name: The name of the source node.
            dst_name: The name of the destination node.
            weight: The edge attribute to use as the weight for shortest path calculation
                    (e.g., 'dis', 'latency'). If None, uses unweighted shortest path (BFS).

        Returns:
            A list of node names representing the shortest path.

        Raises:
            networkx.exception.NetworkXNoPath: If no path exists between the nodes.
            networkx.exception.NetworkXError: If the source or destination node is not in the graph.
        """
        return nx.shortest_path(self.graph, src_name, dst_name, weight=weight)

    def get_shortest_links(self, src_name: str, dst_name: str, weight: Optional[str] = None) -> List[Link]:
        """Retrieve the shortest path as a list of Link objects between two nodes.

        This method first finds the shortest path as a sequence of nodes and then
        retrieves the corresponding Link objects. Assumes a key of 0 for links
        in the shortest path.

        Args:
            src_name: The name of the source node.
            dst_name: The name of the destination node.
            weight: The edge attribute to use as the weight for shortest path calculation.
                    Defaults to None (unweighted).

        Returns:
            A list of Link objects representing the shortest path.

        Raises:
            networkx.exception.NetworkXNoPath: If no path exists between the nodes.
            networkx.exception.NetworkXError: If the source or destination node is not in the graph.
        """
        shortest_path = nx.shortest_path(self.graph, src_name, dst_name, weight=weight)
        return [self.graph.edges[a, b, 0]["data"] for a, b in nx.utils.pairwise(shortest_path)]
    
    def get_graph_diameter(self) -> int:
        """Calculates the diameter of the infrastructure graph.

        The diameter is the longest of all shortest paths between any pair of nodes.
        Assumes the graph is connected.

        Returns:
            The diameter of the graph as an integer (number of edges in the longest shortest path).

        Raises:
            networkx.exception.NetworkXNoPath: If the graph is not connected.
        """
        all_shortest_paths = dict(nx.all_pairs_shortest_path(self.graph))
        return max(len(p) - 1 for val in all_shortest_paths.values() for p in val.values())
