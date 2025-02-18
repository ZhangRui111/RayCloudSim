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

from eval.benchmarks.Pakistan.scenario import Scenario

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
    scenario = Scenario(config_file=f"eval/benchmarks/Pakistan/data/{flag}/config.json", 
                        flag=flag)
    graph = scenario.infrastructure.graph
    
    nx.draw(graph, with_labels=True)
    
    plt.savefig(save_as, dpi=300)

    with open(f"eval/benchmarks/Pakistan/data/source/Tuple30K/ingress.txt", 'r') as f:
        read_lines = f.readlines()
        edge = read_lines[1].split()

        edge = [int(item) - 1 for item in edge]  # RayCloudSim is 0-index
        cloud = read_lines[2].split()
        cloud = [int(item) - 1 for item in cloud]

    if flag == 'Tuple30K':
        seed = 0
        figsize=(8, 8)
    elif flag == 'Tuple50K':
        seed = 10
        figsize=(8, 8)
    elif flag == 'Tuple100K':
        seed = 5
        figsize=(10, 10)
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
        if i in edge:
            node_colors.append(colors['red'])
            node_sizes.append(600)
        elif i in cloud:    
            node_colors.append(colors['blue'])
            node_sizes.append(500)
        else:
            node_colors.append(colors['blue'])
            node_sizes.append(400)

    plt.figure(figsize=figsize)
    nx.draw(
        graph,
        pos=pos,
        node_size=node_sizes,
        node_color=node_colors,
        # node_shape="o",
        # linewidths=1,
        # alpha=1.0,
        with_labels=True,
        # labels=labels,
        # font_size=12,
        # font_color="black",
        # arrows=False,
        # edge_color="black",
        # style="solid",
        # width=1.0,
    )

    plt.savefig(f"{save_as}/{flag}/{flag}_loc.png", dpi=500, bbox_inches='tight')
    
    plt.close()

    
    nx.draw(
        graph,
                with_labels=True,
        node_size=node_sizes,
        node_color=node_colors,
        # node_shape="o",
        # linewidths=1,
        # alpha=1.0,

        # # labels=labels,
        # font_size=12,
        # font_color="black",
        # # arrows=False,
        # edge_color="black",
        # # style="solid",
        # # width=1.0,
    )
    
    plt.savefig(f"{save_as}/{flag}/{flag}.png", dpi=500, bbox_inches='tight')
    # plt.show()
    plt.close()


def main():
    vis_graph('Tuple30K', save_as="eval/benchmarks/Pakistan/data")
    vis_graph('Tuple50K', save_as="eval/benchmarks/Pakistan/data")
    vis_graph('Tuple100K', save_as="eval/benchmarks/Pakistan/data")



if __name__ == '__main__':
    main()
