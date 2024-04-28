import json
import networkx as nx
import matplotlib as mpl
import matplotlib.pyplot as plt

mpl.use('QtAgg')


def plot_graph(graph, config_file, save_as):
    # Load the config file
    with open(config_file, 'r') as fr:
        json_object = json.load(fr)
        json_node = json_object['Node']
        json_edge = json_object['Edge']
        json_target = json_object['Target']
    
    plt.figure(figsize=(8, 8))

    nx.draw(
        graph,
        pos=nx.get_node_attributes(graph, 'pos'),
        node_size=json_node['Basic']['size'],
        node_color=json_node['Basic']['color'],
        node_shape=json_node['Basic']['shape'],
        linewidths=json_node['Basic']['linewidths'],
        alpha=json_node['Basic']['alpha'],
        with_labels=json_node['Basic']['label']=='on',
        labels="",
        font_size=json_node['Label']['fontSize'],
        font_color=json_node['Label']['fontColor'],
        arrows=json_edge['Basic']['arrows']=='true',
        edge_color=json_edge['Basic']['color'],
        style=json_edge['Basic']['style'],
        width=json_edge['Basic']['width'],
    )
    
    # change the color of node boundary
    ax= plt.gca()
    ax.collections[0].set_edgecolor("#000000")
    plt.axis('off')

    plt.savefig(save_as)
    plt.show()
    plt.close()


def vis_graph(env, config_file, save_as):
    """Visualize the topology."""
    plot_graph(env.scenario.infrastructure.graph, config_file, save_as)


def main():
    g = nx.random_geometric_graph(n=10, radius=0.6, dim=2, pos=None, p=2, seed=21)
    plot_graph(g, 
               config_file="core/vis/configs/vis_config_base.json",
               save_as="examples/vis/demo_base.png")
    g.clear()


if __name__ == '__main__':
    main()
