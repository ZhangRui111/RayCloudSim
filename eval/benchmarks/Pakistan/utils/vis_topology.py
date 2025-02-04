import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = current_dir
for _ in range(4):
    parent_dir = os.path.dirname(parent_dir)
sys.path.insert(0, parent_dir)

import networkx as nx
import matplotlib as mpl
import matplotlib.pyplot as plt

from eval.benchmarks.Topo4MEC.scenario import Scenario

mpl.use('QtAgg')


colors = {
    'green': '#8ECFC9',
    'orange': '#FFBE7A',
    'red': '#FA7F6F',
    'blue': '#82B0D2',
    'purple': '#BEB8DC',
    'beige': '#E7DAD2',
    'gray': '#999999',
    'lightgray': '#E9E9E9',
}


def vis_graph(flag, save_as):
    """Visualize all scenarios in Topo4MEC."""
    scenario = Scenario(config_file=f"eval/benchmarks/Topo4MEC/data/{flag}/config.json", 
                        flag=flag)
    graph = scenario.infrastructure.graph

    with open(f"eval/benchmarks/Topo4MEC/source/{flag}/ingress.txt", 'r') as f:
        ingress_line = f.readlines()[1].split()
        ingress_line = [int(item) - 1 for item in ingress_line]  # RayCloudSim is 0-index

    if flag == '25N50E':
        seed = 0
        figsize=(8, 8)
    elif flag == '50N50E':
        seed = 10
        figsize=(8, 8)
    elif flag == '100N150E':
        seed = 5
        figsize=(10, 10)
    elif flag == 'MilanCityCenter':
        seed = 5
        figsize=(8, 8)
    else:
        raise NotImplementedError()
    
    pos = nx.get_node_attributes(graph, 'pos')
    if not pos:
        pos = nx.spring_layout(graph, seed=seed)
    
    labels = {}
    node_colors = []
    node_sizes = []
    for i, (k, _) in enumerate(pos.items()):
        labels[k] = i + 1
        if i in ingress_line:
            node_colors.append(colors['red'])
            node_sizes.append(500)
        else:
            node_colors.append(colors['green'])
            node_sizes.append(400)

    plt.figure(figsize=figsize)
    nx.draw(
        graph,
        pos=pos,
        node_size=node_sizes,
        node_color=node_colors,
        node_shape="o",
        linewidths=1,
        alpha=1.0,
        with_labels=True,
        labels=labels,
        font_size=12,
        font_color="black",
        arrows=False,
        edge_color="black",
        style="solid",
        width=1.0,
    )

    plt.savefig(save_as, dpi=500, bbox_inches='tight')
    # plt.show()
    plt.close()


def main():
    vis_graph('25N50E', save_as="eval/benchmarks/Topo4MEC/data/25N50E/25N50E.png")
    vis_graph('50N50E', save_as="eval/benchmarks/Topo4MEC/data/50N50E/50N50E.png")
    vis_graph('100N150E', save_as="eval/benchmarks/Topo4MEC/data/100N150E/100N150E.png")
    vis_graph('MilanCityCenter', 
              save_as="eval/benchmarks/Topo4MEC/data/MilanCityCenter/MilanCityCenter.png")


if __name__ == '__main__':
    main()
