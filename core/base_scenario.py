import json

from abc import ABCMeta, abstractmethod
from typing import Optional, Union, Tuple, List

from core.infrastructure import Infrastructure, Link, DataFlow, Node, Location

__all__ = ["BaseScenario"]


class BaseScenario(metaclass=ABCMeta):
    """The base class of customized scenarios."""

    def __init__(self, config_file):
        # Load the config file
        with open(config_file, 'r') as fr:
            json_object = json.load(fr)
            self.json_nodes, self.json_edges = json_object['Nodes'], json_object['Edges']
        
        self.infrastructure = Infrastructure()
        self.node_id2name = dict()

        self.init_infrastructure_nodes()
        self.init_infrastructure_links()

    def init_infrastructure_nodes(self):
        """Initialize nodes in the infrastructure.

        Note:
            Node id must be **strictly increasing from zero**, i.e., 0, 1, ...
            Node name is user-defined.
        """
        # keys = ['NodeType', 'NodeName', 'NodeId', 'MaxCpuFreq', 'MaxBufferSize', 
        #         'LocX', 'LocY', 'IdleEnergyCoef', 'ExeEnergyCoef', ]
        for node_info in self.json_nodes:

            assert node_info['NodeType'] == 'Node', \
            f"Unrecognized NodeType {node_info['NodeType']}; \
              One possible solution is to overwrite the init_infrastructure_nodes()"

            self.infrastructure.add_node(
                Node(node_id=node_info['NodeId'], 
                     name=node_info['NodeName'], 
                     max_cpu_freq=node_info['MaxCpuFreq'], 
                     max_buffer_size=node_info['MaxBufferSize'], 
                     location=Location(node_info['LocX'], node_info['LocY']),
                     idle_energy_coef=node_info['IdleEnergyCoef'], 
                     exe_energy_coef=node_info['ExeEnergyCoef']))
            self.node_id2name[node_info['NodeId']] = node_info['NodeName']

    def init_infrastructure_links(self):
        """Initialize links in the infrastructure."""
        # keys = ['SrcNodeID', 'DstNodeID', 'Bandwidth']
        for edge_info in self.json_edges:

            assert edge_info['EdgeType'] == 'Link', \
            f"Unrecognized EdgeType {edge_info['EdgeType']}; \
              One possible solution is to overwrite the init_infrastructure_links()"

            self.add_bilateral_links(self.node_id2name[edge_info['SrcNodeID']],
                                     self.node_id2name[edge_info['DstNodeID']], 
                                     edge_info['Bandwidth'])

    @abstractmethod
    def status(self, node_name: Optional[str] = None,
               link_args: Optional[Tuple] = None):
        """User-defined Scenario status."""
        nodes = self.nodes()
        links = self.links()
        return nodes, links

    def get_node(self, name):
        return self.infrastructure.get_node(name)

    def get_link(self, src_name: str, dst_name: str, key=0):
        return self.infrastructure.get_link(src_name, dst_name, key)

    def nodes(self):
        return self.infrastructure.nodes()

    def links(self):
        return self.infrastructure.links()

    def add_unilateral_link(self, src_name: str, dst_name: str, bandwidth: float,
                            base_latency: Optional[float] = 0):
        """Add an unilateral link in the infrastructure."""
        self.infrastructure.add_link(
            Link(self.infrastructure.get_node(src_name),
                 self.infrastructure.get_node(dst_name),
                 max_bandwidth=bandwidth, base_latency=base_latency)
        )

    def add_bilateral_links(self, src_name: str, dst_name: str, bandwidth: Union[float, List],
                            base_latency: Optional[float] = 0):
        """Add a bilateral link in the infrastructure."""
        self.infrastructure.add_link(
            Link(self.infrastructure.get_node(src_name),
                 self.infrastructure.get_node(dst_name),
                 max_bandwidth=bandwidth[0] if isinstance(bandwidth, List) else bandwidth,
                 base_latency=base_latency)
        )
        self.infrastructure.add_link(
            Link(self.infrastructure.get_node(dst_name),
                 self.infrastructure.get_node(src_name),
                 max_bandwidth=bandwidth[1] if isinstance(bandwidth, List) else bandwidth,
                 base_latency=base_latency)
        )

    def reset(self):
        """Remove all tasks and data flows in the infrastructure."""
        for node in self.nodes():
            node.reset()
            # for wireless nodes
            if node.flag_only_wireless:
                node.update_access_dst_nodes(self.nodes())

        for link in self.links():
            link.reset()

    def send_data_flow(self, data_flow: DataFlow, links=None,
                       src_name: str = None, dst_name: str = None, weight=None):
        """Simulate a data flow in the infrastructure.

        Send a data flow from the src node to the dst node.
        """
        if not links:
            links = self.infrastructure.get_shortest_links(src_name, dst_name, weight)
        data_flow.allocate(links)
