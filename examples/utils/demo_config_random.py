import os
import sys

PROJECT_NAME = 'RayCloudSim'
cur_path = os.path.abspath(os.path.dirname(__file__))
root_path = cur_path
while os.path.split(os.path.split(root_path)[0])[-1] != PROJECT_NAME:
    root_path = os.path.split(root_path)[0]
root_path = os.path.split(root_path)[0]
sys.path.append(root_path)

import json
import networkx as nx
import random


def nodes_and_edges_from_graph(graph, save_as):
    """Extract info of nodes and edges from a networkx graph."""
    # 1. nodes
    # keys = ['NodeType', 'NodeName', 'NodeId', 'MaxCpuFreq', 'MaxBufferSize', 
    #         'LocX', 'LocY', 'IdleEnergyCoef', 'ExeEnergyCoef', ]
    nodes = []
    for node_id in graph.nodes():
        x, y = graph.nodes[node_id]['pos']
        
        idle_energy_coef = 0.1 * random.random()
        exe_energy_coef = 10 * idle_energy_coef

        nodes.append(
            {
                'NodeType': 'Node',
                'NodeName': f'n{node_id}',
                'NodeId': node_id,
                'MaxCpuFreq': random.randint(5, 30),
                'MaxBufferSize': random.randint(10, 400),
                'LocX': round(100 * x, 2),
                'LocY': round(100 * y, 2),
                'IdleEnergyCoef': round(idle_energy_coef, 2),
                'ExeEnergyCoef': round(exe_energy_coef, 2),
            }
        )

    # 2. edges
    # keys = ['EdgeType', 'SrcNodeID', 'DstNodeID', 'Bandwidth']
    edges = []
    for src, dst in graph.edges():
        bandwidth = 100  # bandwidth
        edges.append(
            {
                'EdgeType': 'Link', 
                'SrcNodeID': src, 
                'DstNodeID': dst, 
                'Bandwidth': bandwidth,
            }
        )

    # 3. saving
    data = {
        'Nodes': nodes,
        'Edges': edges,
    }
    json_object = json.dumps(data, indent=4)
    if not os.path.exists(save_as):
        with open(save_as, 'w+') as fw:
            fw.write(json_object)
    else:
        print("File already exists!")

    # 4. loading
    with open(save_as, 'r') as fr:
        json_object = json.load(fr)
        nodes, edges = json_object['Nodes'], json_object['Edges']

    print(f"{len(nodes)} nodes, {len(edges)} edges")


def main():
    # Randomly generate a small network and save all parameters
    graph = nx.random_geometric_graph(n=10, radius=0.6, dim=2, pos=None, p=2, seed=21)
    nodes_and_edges_from_graph(graph, save_as="examples/scenarios/configs/config_3.json")

    # Randomly generate a small network and save all parameters
    graph = nx.random_geometric_graph(n=20, radius=0.3, dim=2, pos=None, p=2, seed=0)
    nodes_and_edges_from_graph(graph, save_as="eval/benchmarks/caseA/small/config.json")


if __name__ == '__main__':
    main()
