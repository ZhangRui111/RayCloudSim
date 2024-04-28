import numpy as np

from core.base_scenario import BaseScenario


class Scenario(BaseScenario):

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
        n = len(self.get_nodes())
        node_max_cpu_freq = np.zeros(n)
        node_free_cpu_freq = np.zeros(n)
        link_max_bandwidth = np.zeros((n, n))
        link_free_bandwidth = np.zeros((n, n))

        for _, node in self.get_nodes().items():
            node_max_cpu_freq[node.node_id] = node.max_cpu_freq
            node_free_cpu_freq[node.node_id] = node.free_cpu_freq

        for _, link in self.get_links().items():
            link_max_bandwidth[link.src.node_id][link.dst.node_id] = link.max_bandwidth
            link_free_bandwidth[link.src.node_id][link.dst.node_id] = link.free_bandwidth

        return node_max_cpu_freq, node_free_cpu_freq, link_max_bandwidth, link_free_bandwidth
