import os
import sys

PROJECT_NAME = 'RayCloudSim'
cur_path = os.path.abspath(os.path.dirname(__file__))
root_path = cur_path
while os.path.split(os.path.split(root_path)[0])[-1] != PROJECT_NAME:
    root_path = os.path.split(root_path)[0]
root_path = os.path.split(root_path)[0]
sys.path.append(root_path)

import numpy as np
import networkx as nx
import random

from core.base_scenario import BaseScenario
from core.infrastructure import Node, Location


class Scenario(BaseScenario):

    def init_infrastructure_nodes(self):
        with open("examples/scenarios/random_topology.txt", 'r') as fr:
            nodes, _ = eval(fr.read())

        for node_id, name, max_cpu_freq, max_buffer_size, \
            loc_x, loc_y, idle_power_coef, exe_power_coef in nodes:
            self.infrastructure.add_node(
                Node(node_id=node_id, name=name, 
                     max_cpu_freq=max_cpu_freq, max_buffer_size=max_buffer_size, 
                     location=Location(loc_x, loc_y),
                     idle_power_coef=idle_power_coef, exe_power_coef=exe_power_coef))
            self.node_id2name[node_id] = name

    def init_infrastructure_links(self):
        with open("examples/scenarios/random_topology.txt", 'r') as fr:
            _, edges = eval(fr.read())

        for src, dst, bandwidth in edges:
            self.add_bilateral_links(self.node_id2name[src],
                                     self.node_id2name[dst], bandwidth)

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


def nodes_and_edges_from_graph(graph):
    """Extract info of nodes and edges from a networkx graph."""
    # 1. nodes
    nodes = []
    for node_id in graph.nodes():
        x, y = graph.nodes[node_id]['pos']
        
        idle_power_coef = 0.1 * random.random()
        exe_power_coef = 10 * idle_power_coef
        nodes.append((node_id,  # node id
                      f'n{node_id}',  # node name 
                      random.randint(5, 30),  # max_cpu_freq
                      random.randint(10, 400),  # max_buffer_size
                      round(100 * x, 2),  # loc_x
                      round(100 * y, 2),  # loc_y
                      round(idle_power_coef, 2),  # idle_power_coef
                      round(exe_power_coef, 2)))  # exe_power_coef

    # 2. edges
    edges = []
    for src, dst in graph.edges():
        bandwidth = 100  # bandwidth
        edges.append((src, dst, bandwidth))

    # 3. saving
    if not os.path.exists("examples/scenarios/random_topology.txt"):
        with open("examples/scenarios/random_topology.txt", 'w+') as fw:
            fw.write(str([nodes, edges]))
    else:
        print("File already exists!")

    # 4. loading
    with open("examples/scenarios/random_topology.txt", 'r') as fr:
        nodes, edges = eval(fr.read())

    print(f"{len(nodes)} nodes, {len(edges)} edges")


def main():
    # Randomly generate a small network and save all parameters
    graph = nx.random_geometric_graph(n=10, radius=0.6, dim=2, pos=None,
                                      p=2, seed=21)
    nodes_and_edges_from_graph(graph)


if __name__ == '__main__':
    main()
