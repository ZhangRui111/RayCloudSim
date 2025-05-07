import json
from abc import ABCMeta, abstractmethod
from typing import Optional, Union, Tuple, List

from core.infrastructure import Infrastructure
from core.link import Link
from core.node import Node
from core.utils import Location, DataFlow

__all__ = ["BaseScenario"]


class BaseScenario(metaclass=ABCMeta):
    """
    Base class for customized scenarios in the RayCloudSim simulation.

    This class provides the fundamental structure and methods for setting up
    and managing the simulation infrastructure, including nodes and links,
    based on a configuration file.
    """

    def __init__(self, config_file: str):
        """
        Initialize the scenario by loading the configuration file and setting up the infrastructure.

        Args:
            config_file: The path to the JSON configuration file.
        """
        # Load the configuration from the specified file
        self.json_object = self.load_config(config_file)
        # Extract node and edge information from the loaded configuration
        self.json_nodes, self.json_edges = self.json_object['Nodes'], self.json_object['Edges']

        # Initialize the infrastructure and a mapping from node ID to node name
        self.infrastructure = Infrastructure()
        self.node_id2name = {}

        # Initialize the infrastructure with nodes and links based on the configuration
        self.init_infrastructure_nodes()
        self.init_infrastructure_links()

    def load_config(self, config_file: str) -> dict:
        """Load the configuration file and return its content as a JSON object."""
        with open(config_file, 'r') as fr:
            return json.load(fr)

    def init_infrastructure_nodes(self):
        """
        Initialize nodes in the infrastructure based on the loaded configuration.

        This method iterates through the 'Nodes' section of the configuration,
        creates Node objects, and adds them to the infrastructure.
        It also populates the node_id2name mapping.
        """
        for node_info in self.json_nodes:
            # Ensure the node type is 'Node' or handle custom initialization in subclasses
            assert node_info['NodeType'] == 'Node', (
                f"Invalid NodeType {node_info['NodeType']}. "
                "Ensure it is 'Node' or override init_infrastructure_nodes()."
            )

            # Get the location of the node if coordinates are provided
            location = self.get_location(node_info)
            # Create a Node object with information from the configuration
            node = Node(
                id=node_info['NodeId'],
                name=node_info['NodeName'],
                max_cpu_freq=node_info['MaxCpuFreq'],
                max_buffer_size=node_info['MaxBufferSize'],
                location=location,
                energy_coefficients={
                    'idle': node_info['IdleEnergyCoef'],
                    'exe': node_info['ExeEnergyCoef'], 
                }
            )

            # Add the created node to the infrastructure
            self.infrastructure.add_node(node)
            # Map the node ID to its name for easy lookup
            self.node_id2name[node_info['NodeId']] = node_info['NodeName']

    def get_location(self, node_info: dict) -> Optional[Location]:
        """Return a Location object if coordinates ('LocX', 'LocY') are provided in node_info, 
        otherwise None."""
        if 'LocX' in node_info and 'LocY' in node_info:
            return Location(node_info['LocX'], node_info['LocY'])
        return None

    def init_infrastructure_links(self):
        """
        Initialize links between nodes in the infrastructure based on the loaded configuration.

        This method iterates through the 'Edges' section of the configuration,
        creates Link objects, and adds them to the infrastructure. It handles
        both unilateral ('SingleLink') and bilateral ('Link') connections.
        """
        for edge_info in self.json_edges:
            # Ensure the edge type is valid
            assert edge_info['EdgeType'] in ['Link', 'SingleLink'], (
                f"Invalid EdgeType {edge_info['EdgeType']}. "
                "Ensure it is either 'Link' or 'SingleLink'."
            )

            # Get source and destination node IDs and calculate base latency
            src_node_id, dst_node_id = edge_info['SrcNodeID'], edge_info['DstNodeID']
            base_latency = self._calculate_base_latency(edge_info)

            # Add links based on the edge type
            if edge_info['EdgeType'] == 'SingleLink':
                self.add_unilateral_link(
                    self.node_id2name[src_node_id],
                    self.node_id2name[dst_node_id],
                    edge_info['Bandwidth'],
                    base_latency
                )
            else:
                self.add_bilateral_links(
                    self.node_id2name[src_node_id],
                    self.node_id2name[dst_node_id],
                    edge_info['Bandwidth'],
                    base_latency
                )

    def _calculate_base_latency(self, edge_info: dict, 
                                src_node_id: int = None, dst_node_id: int = None) -> float:
        """
        Calculate the base latency for the link.

        If 'BaseLatency' is provided in the edge information, it is used.
        Otherwise, the base latency is calculated (currently returns 0 if not provided).

        Args:
            edge_info: A dictionary containing the edge's information.

        Returns:
            The base latency for the link.
        """
        if 'BaseLatency' in edge_info:
            return edge_info['BaseLatency']

        # Optional: Implement base latency calculation based on node distances if not provided in config
        return 0

    @abstractmethod
    def status(self, node_name: Optional[str] = None, link_args: Optional[Tuple] = None):
        """
        Abstract method to define the scenario's status.

        Subclasses must implement this method to provide specific status information
        relevant to the scenario.

        Args:
            node_name: Optional name of a specific node to get status for.
            link_args: Optional tuple containing arguments to identify a specific link.

        Returns:
            Scenario-specific status information.
        """
        # Example implementation (can be overridden by subclasses)
        nodes = self.get_nodes()
        links = self.get_links()
        return nodes, links

    def avg_node_energy(self, node_name_list: Optional[List[str]] = None) -> float:
        """
        Calculate the average energy consumption of specified nodes.

        Args:
            node_name_list: A list of node names. If None, calculate for all nodes.

        Returns:
            The average energy consumption.
        """
        if not node_name_list:
            node_list = self.get_nodes().values()
        else:
            node_list = [self.get_node(node_name) for node_name in node_name_list]

        total_energy = sum(node.energy_consumption for node in node_list)
        return total_energy / len(node_list) if node_list else 0

    def node_energy(self, node_name: str) -> float:
        """
        Return the energy consumption of a specific node.

        Args:
            node_name: The name of the node.

        Returns:
            The energy consumption of the node.
        """
        return self.get_node(node_name).energy_consumption

    def get_node(self, name: str) -> Node:
        """
        Return the node by its name.

        Args:
            name: The name of the node.

        Returns:
            The Node object.
        """
        return self.infrastructure.get_node(name)

    def get_link(self, src_name: str, dst_name: str, key=0) -> Link:
        """
        Return the link between two nodes.

        Args:
            src_name: The name of the source node.
            dst_name: The name of the destination node.
            key: Optional key to identify a specific link between the nodes (for multi-graphs).

        Returns:
            The Link object.
        """
        return self.infrastructure.get_link(src_name, dst_name, key)

    def get_nodes(self):
        """Return all nodes in the infrastructure."""
        return self.infrastructure.get_nodes()

    def get_links(self):
        """Return all links in the infrastructure."""
        return self.infrastructure.get_links()

    def add_unilateral_link(self, src_name: str, dst_name: str, bandwidth: float, base_latency: float = 0):
        """
        Add a unilateral link between two nodes.

        Args:
            src_name: The name of the source node.
            dst_name: The name of the destination node.
            bandwidth: The maximum bandwidth of the link.
            base_latency: The base latency of the link (default is 0).
        """
        self.infrastructure.add_link(
            Link(self.infrastructure.get_node(src_name), self.infrastructure.get_node(dst_name),
                 max_bandwidth=bandwidth, base_latency=base_latency)
        )

    def add_bilateral_links(
        self, src_name: str, dst_name: str, bandwidth: Union[float, List], base_latency: float = 0
    ):
        """
        Add bilateral links between two nodes.

        This creates two links: one from src to dst and one from dst to src.
        Bandwidth can be a single float (for symmetric links) or a list of two floats
        [bandwidth_src_to_dst, bandwidth_dst_to_src].

        Args:
            src_name: The name of the first node.
            dst_name: The name of the second node.
            bandwidth: The maximum bandwidth(s) of the links.
            base_latency: The base latency of the links (default is 0).
        """
        # Add link from source to destination
        self.infrastructure.add_link(
            Link(self.infrastructure.get_node(src_name), self.infrastructure.get_node(dst_name),
                 max_bandwidth=bandwidth[0] if isinstance(bandwidth, List) else bandwidth,
                 base_latency=base_latency)
        )
        # Add link from destination to source
        self.infrastructure.add_link(
            Link(self.infrastructure.get_node(dst_name), self.infrastructure.get_node(src_name),
                 max_bandwidth=bandwidth[1] if isinstance(bandwidth, List) else bandwidth,
                 base_latency=base_latency)
        )

    def reset(self):
        """
        Reset all nodes and links in the infrastructure to their initial state.

        This method is typically called at the beginning of each simulation step
        or episode.
        """
        for node in self.get_nodes().values():
            node.reset()

        for link in self.get_links().values():
            link.reset()

    def send_data_flow(self, data_flow: DataFlow, links=None, src_name: str = None, 
                       dst_name: str = None, weight=None):
        """
        Simulate a data flow in the infrastructure from source to destination.

        Args:
            data_flow: The DataFlow object to simulate.
            links: Optional list of links for the data flow to traverse. If None,
                   the shortest path between src_name and dst_name is used.
            src_name: The name of the source node (required if links is None).
            dst_name: The name of the destination node (required if links is None).
            weight: Optional weight function for shortest path calculation.
        """
        # If no specific links are provided, find the shortest path
        if not links:
            links = self.infrastructure.get_shortest_links(src_name, dst_name, weight)
        # Allocate the data flow to the specified or found links
        data_flow.allocate(links)
