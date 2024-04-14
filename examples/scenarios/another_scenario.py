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
            Node(node_id=0, name='n0', 
                 max_cpu_freq=5, max_buffer_size=100,
                 location=Location(16, 68),
                 idle_power_coef=0.01, exe_power_coef=1))
        self.infrastructure.add_node(
            Node(node_id=1, name='n1', 
                 max_cpu_freq=5, max_buffer_size=100,
                 location=Location(63, 47),
                 idle_power_coef=0.01, exe_power_coef=1))
        self.infrastructure.add_node(
            Node(node_id=2, name='n2', 
                 max_cpu_freq=5, max_buffer_size=100,
                 location=Location(30, 30),
                 idle_power_coef=0.01, exe_power_coef=1))
        self.infrastructure.add_node(
            Node(node_id=3, name='n3', 
                 max_cpu_freq=5, max_buffer_size=100,
                 location=Location(15, 45),
                 idle_power_coef=0.01, exe_power_coef=1))

    def init_infrastructure_links(self):
        self.add_bilateral_links(self.node_id2name[0],
                                 self.node_id2name[1], 15)
        self.add_bilateral_links(self.node_id2name[1],
                                 self.node_id2name[2], 15)

    def status(self, node_name=None, link_args=None):
        # Return status of specific Node/Link
        if node_name and link_args:
            node = self.get_node(node_name)
            link = self.get_link(*link_args)
            node_status = [node.max_cpu_freq, node.free_cpu_freq]
            link_statue = [link.max_bandwidth, link.free_bandwidth]
            return node_status, link_statue
        if node_name:
            node = self.get_node(node_name)
            node_status = [node.max_cpu_freq, node.free_cpu_freq]
            return node_status
        if link_args:
            link = self.get_link(*link_args)
            link_statue = [link.max_bandwidth, link.free_bandwidth]
            return link_statue

        # Return status of the whole scenario
        n = len(self.nodes())
        node_max_cpu_freq = np.zeros(n)
        node_free_cpu_freq = np.zeros(n)
        link_max_bandwidth = np.zeros((n, n))
        link_free_bandwidth = np.zeros((n, n))

        for node in self.nodes():
            node_max_cpu_freq[node.node_id] = node.max_cpu_freq
            node_free_cpu_freq[node.node_id] = node.free_cpu_freq

        for link in self.links():
            link_max_bandwidth[link.src.node_id][link.dst.node_id] = link.max_bandwidth
            link_free_bandwidth[link.src.node_id][link.dst.node_id] = link.free_bandwidth

        return node_max_cpu_freq, node_free_cpu_freq, link_max_bandwidth, link_free_bandwidth
