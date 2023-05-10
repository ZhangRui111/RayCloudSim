import numpy as np

from core.base_scenario import BaseScenario
from core.infrastructure import Node, Location


class Scenario(BaseScenario):
    """A simple scenario with 4 nodes.

    3 connected nodes and 1 isolated node.
    """

    def init_infrastructure_nodes(self):
        self.node_id2name[0] = 'n0'
        self.node_id2name[1] = 'n1'
        self.node_id2name[2] = 'n2'
        self.node_id2name[3] = 'n3'

        self.infrastructure.add_node(
            Node(node_id=0, name='n0', cu=20,
                 location=Location(16, 68)))
        self.infrastructure.add_node(
            Node(node_id=1, name='n1', cu=20,
                 location=Location(63, 47)))
        self.infrastructure.add_node(
            Node(node_id=2, name='n2', cu=20,
                 location=Location(30, 30)))
        self.infrastructure.add_node(
            Node(node_id=3, name='n3',
                 location=Location(15, 45)))

    def init_infrastructure_links(self):
        self.add_bilateral_links(self.node_id2name[0],
                                 self.node_id2name[1], 20)
        self.add_bilateral_links(self.node_id2name[1],
                                 self.node_id2name[2], 20)

    def status(self, node_name=None, link_args=None):
        # Return status of specific Node/Link
        if node_name and link_args:
            node = self.get_node(node_name)
            link = self.get_link(*link_args)
            node_status = [node.cu, node.used_cu]
            link_statue = [link.bandwidth, link.used_bandwidth]
            return node_status, link_statue
        if node_name:
            node = self.get_node(node_name)
            node_status = [node.cu, node.used_cu]
            return node_status
        if link_args:
            link = self.get_link(*link_args)
            link_statue = [link.bandwidth, link.used_bandwidth]
            return link_statue

        # Return status of the whole scenario
        n = len(self.nodes())
        node_cu = np.zeros(n)
        node_used_cu = np.zeros(n)
        link_bandwidth = np.zeros((n, n))
        link_used_bandwidth = np.zeros((n, n))

        for node in self.nodes():
            node_cu[node.node_id] = node.cu
            node_used_cu[node.node_id] = node.used_cu

        for link in self.links():
            link_bandwidth[link.src.node_id][link.dst.node_id] = \
                link.bandwidth
            link_used_bandwidth[link.src.node_id][link.dst.node_id] = \
                link.used_bandwidth

        return node_cu, node_used_cu, link_bandwidth, link_used_bandwidth
