import os
import json
import random


def main():
    # 1. loading source files
    flag, n = '25N50E', 25
    # flag, n = '50N50E', 50
    # flag, n = '100N150E', 100
    # flag, n = 'MilanCityCenter', 30
    with open(f"eval/benchmarks/Topo4MEC/source/{flag}/graph.txt", 'r') as f:
        graph_lines = f.readlines()
        edges_lines = [line.split() for line in graph_lines]
        edges_lines = [[int(line[0]) - 1, int(line[1]) - 1, float(line[2])]
                       for line in edges_lines]  # RayCloudSim is 0-index
    save_as = f"eval/benchmarks/Topo4MEC/data/{flag}/config.json"

    # 2. nodes & edges
    # keys = ['NodeType', 'NodeName', 'NodeId', 'MaxCpuFreq', 'MaxBufferSize', 
    #         'IdleEnergyCoef', 'ExeEnergyCoef', ]
    nodes = []
    for node_id in range(n):

        idle_energy_coef = max(0.01 * random.random(), 0.001)
        exe_energy_coef = 10 * idle_energy_coef

        nodes.append(
            {
                'NodeType': 'Node',
                'NodeName': f'n{node_id}',
                'NodeId': node_id,
                'MaxCpuFreq': random.randint(10, 50) * 100,  # MHz, 1 GHz = 1000 MHz
                'MaxBufferSize': random.randint(5, 40) * 10,  # Mb
                'IdleEnergyCoef': round(idle_energy_coef, 4),
                'ExeEnergyCoef': round(exe_energy_coef, 4),
            }
        )
    # keys = ['EdgeType', 'SrcNodeID', 'DstNodeID', 'Bandwidth']
    edges = []
    for src, dst, bw in edges_lines:
        edges.append(
            {
                'EdgeType': 'SingleLink', 
                'SrcNodeID': src,
                'DstNodeID': dst, 
                'Bandwidth': 10 * bw,  # Mbps
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


if __name__ == '__main__':
    main()
