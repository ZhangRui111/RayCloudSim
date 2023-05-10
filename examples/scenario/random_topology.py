import numpy as np
import networkx as nx
import os
import random

from core.base_scenario import BaseScenario
from core.infrastructure import Node, Location


class Scenario(BaseScenario):

    def init_infrastructure_nodes(self):
        with open("examples/scenario/random_topology.txt", 'r') as fr:
            nodes, _ = eval(fr.read())

        for node_id, name, cu, loc_x, loc_y in nodes:
            self.infrastructure.add_node(
                Node(node_id=node_id, name=name, cu=cu,
                     location=Location(loc_x, loc_y)))
            self.node_id2name[node_id] = name

    def init_infrastructure_links(self):
        with open("examples/scenario/random_topology.txt", 'r') as fr:
            _, edges = eval(fr.read())

        for src, dst, bandwidth in edges:
            self.add_bilateral_links(self.node_id2name[src],
                                     self.node_id2name[dst], bandwidth)

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


def nodes_and_edges_from_graph(graph):
    """Extract info of nodes and edges from a networkx graph."""
    # 1. nodes
    nodes = []
    for node_id in graph.nodes():
        x, y = graph.nodes[node_id]['pos']
        # (node_id, name, cu, location.x, location.y)
        nodes.append((node_id, f'n{node_id}',
                      random.randint(10, 50),
                      round(100 * x, 2), round(100 * y, 2)))

    # 2. edges
    edges = []
    for src, dst in graph.edges():
        bandwidth = 100  # bandwidth
        edges.append((src, dst, bandwidth))

    # 3. saving
    if not os.path.exists("random_topology.txt"):
        with open("random_topology.txt", 'w+') as fw:
            fw.write(str([nodes, edges]))
    else:
        print("File already exists!")

    # # 4. loading
    # with open("random_topology.txt", 'r') as fr:
    #     nodes, edges = eval(fr.read())

    print(f"{len(nodes)} nodes, {len(edges)} edges")


def main():
    # Randomly generate a small network and save all parameters
    graph = nx.random_geometric_graph(n=10, radius=0.6, dim=2, pos=None,
                                      p=2, seed=21)
    nodes_and_edges_from_graph(graph)


if __name__ == '__main__':
    main()
