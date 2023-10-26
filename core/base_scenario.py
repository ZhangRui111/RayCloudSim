from abc import ABCMeta, abstractmethod
from typing import Optional, Tuple

from core.infrastructure import Infrastructure, Link, DataFlow

__all__ = ["BaseScenario"]


class BaseScenario(metaclass=ABCMeta):
    """The base class of customized scenario."""

    def __init__(self):
        self.infrastructure = Infrastructure()
        self.node_id2name = dict()

        self.init_infrastructure_nodes()
        self.init_infrastructure_links()

    @abstractmethod
    def init_infrastructure_nodes(self):
        """Initialize nodes in the infrastructure.

        Note:
            Node id must be **strictly increasing from zero**, i.e., 0, 1, ...
            Node name is user-defined.
        """
        pass

    @abstractmethod
    def init_infrastructure_links(self):
        """Initialize links in the infrastructure."""
        pass

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

    def add_unilateral_link(self, src_name: str, dst_name: str, bandwidth: int,
                            base_latency: Optional[float] = 0):
        """Add an unilateral link in the infrastructure."""
        self.infrastructure.add_link(
            Link(self.infrastructure.get_node(src_name),
                 self.infrastructure.get_node(dst_name),
                 bandwidth=bandwidth, base_latency=base_latency)
        )

    def add_bilateral_links(self, src_name: str, dst_name: str, bandwidth: int,
                            base_latency: Optional[float] = 0):
        """Add a bilateral link in the infrastructure."""
        self.infrastructure.add_link(
            Link(self.infrastructure.get_node(src_name),
                 self.infrastructure.get_node(dst_name),
                 bandwidth=bandwidth, base_latency=base_latency)
        )
        self.infrastructure.add_link(
            Link(self.infrastructure.get_node(dst_name),
                 self.infrastructure.get_node(src_name),
                 bandwidth=bandwidth, base_latency=base_latency)
        )

    def reset(self):
        """Remove all tasks and data flows in the infrastructure."""
        for node in self.nodes():
            node.tasks = []
            node.used_cu = 0
            node.buffer.clear()
            node.used_buffer = 0
            # for wireless nodes
            if node.flag_only_wireless:
                node.update_access_dst_nodes(self.nodes())

        for link in self.links():
            link.data_flows = []
            link.used_bandwidth = 0

    def send_data_flow(self, data_flow: DataFlow, links=None,
                       src_name: str = None, dst_name: str = None, weight=None):
        """Simulate a data flow in the infrastructure.

        Send a data flow from the src node to the dst node.
        """
        if not links:
            links = self.infrastructure.get_shortest_links(src_name, dst_name,
                                                           weight)
        data_flow.allocate(links)
