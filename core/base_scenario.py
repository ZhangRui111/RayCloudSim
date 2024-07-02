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
            self.json_object = json.load(fr)
        self.json_nodes, self.json_edges = self.json_object['Nodes'], self.json_object['Edges']
        
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
            
            if 'LocX' in node_info.keys() and 'LocY' in node_info.keys():
                location=Location(node_info['LocX'], node_info['LocY'])
            else:
                location = None
            
            self.infrastructure.add_node(
                Node(node_id=node_info['NodeId'], 
                     name=node_info['NodeName'], 
                     max_cpu_freq=node_info['MaxCpuFreq'], 
                     max_buffer_size=node_info['MaxBufferSize'], 
                     location=location,
                     idle_energy_coef=node_info['IdleEnergyCoef'], 
                     exe_energy_coef=node_info['ExeEnergyCoef']))
            self.node_id2name[node_info['NodeId']] = node_info['NodeName']

    def init_infrastructure_links(self):
        """Initialize links in the infrastructure."""
        # keys = ['SrcNodeID', 'DstNodeID', 'Bandwidth']
        for edge_info in self.json_edges:

            assert edge_info['EdgeType'] in ['Link', 'SingleLink'], \
            f"Unrecognized EdgeType {edge_info['EdgeType']}; \
              One possible solution is to overwrite the init_infrastructure_links()"
            
            if edge_info['EdgeType'] == 'SingleLink':
                self.add_unilateral_link(self.node_id2name[edge_info['SrcNodeID']],
                                         self.node_id2name[edge_info['DstNodeID']], 
                                         edge_info['Bandwidth'])
            else:
                self.add_bilateral_links(self.node_id2name[edge_info['SrcNodeID']],
                                        self.node_id2name[edge_info['DstNodeID']], 
                                        edge_info['Bandwidth'])

    @abstractmethod
    def status(self, node_name: Optional[str] = None,
               link_args: Optional[Tuple] = None):
        """User-defined Scenario status."""
        nodes = self.get_nodes()
        links = self.get_links()
        return nodes, links

    def get_node(self, name):
        return self.infrastructure.get_node(name)

    def get_link(self, src_name: str, dst_name: str, key=0):
        return self.infrastructure.get_link(src_name, dst_name, key)

    def get_nodes(self):
        return self.infrastructure.get_nodes()

    def get_links(self):
        return self.infrastructure.get_links()

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
        for node in self.get_nodes().values():
            node.reset()
            # for wireless nodes
            if node.flag_only_wireless:
                node.update_access_dst_nodes(self.get_nodes())

        for link in self.get_links().values():
            link.reset()

    def send_data_flow(self, data_flow: DataFlow, links=None,
                       src_name: str = None, dst_name: str = None, weight=None):
        """Simulate a data flow in the infrastructure.

        Send a data flow from the src node to the dst node.
        """
        if not links:
            links = self.infrastructure.get_shortest_links(src_name, dst_name, weight)
        data_flow.allocate(links)
