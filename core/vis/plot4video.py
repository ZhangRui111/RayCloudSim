import json
import networkx as nx
import matplotlib as mpl
import matplotlib.pyplot as plt

mpl.use('QtAgg')


def plot_frame(graph, values, config_file, save_as):

    # Load the config file
    with open(config_file, 'r') as fr:
        json_object = json.load(fr)
        json_node = json_object['Node']
        json_edge = json_object['Edge']
        json_target = json_object['Target']
    
    node_data = nx.get_node_attributes(graph, 'data')
    labels = {k: v.node_id for k, v in node_data.items()}
    if json_node['Basic']['colorWeight'] == 'on':
        node_color = [v for k, v in values['node'].items()]
        node_cmap = plt.cm.get_cmap(json_node['ColorWeight']['cmap'])
    else:
        node_color = json_node['Basic']['color']
        node_cmap = None

    if json_edge['Basic']['colorWeight'] == 'on':
        edge_color = [v for k, v in values['edge'].items()]
        edge_cmap = plt.cm.get_cmap(json_edge['ColorWeight']['cmap'])
    else:
        edge_color = json_edge['Basic']['color']
        edge_cmap = None
    
    plt.figure(figsize=(8, 8))
    plt.title(f"{values['now']}")

    nx.draw_networkx_nodes(
        graph,
        pos=nx.get_node_attributes(graph, 'pos'),
        node_size=json_node['Basic']['size'],
        node_color=node_color,
        cmap=node_cmap,
        node_shape=json_node['Basic']['shape'],
        linewidths=json_node['Basic']['linewidths'],
        alpha=json_node['Basic']['alpha'],
    )
    
    if json_node['Basic']['label'] == 'on':
        nx.draw_networkx_labels(
            graph,
            pos=nx.get_node_attributes(graph, 'pos'),
            labels=labels,
            font_size=json_node['Label']['fontSize'],
            font_color=json_node['Label']['fontColor'],
        )
    
    nx.draw_networkx_edges(
        graph,
        pos=nx.get_node_attributes(graph, 'pos'),
        arrows=json_edge['Basic']['arrows']=='true',
        edge_color=edge_color,
        edge_cmap = edge_cmap,
        style=json_edge['Basic']['style'],
        width=json_edge['Basic']['width'],
    )

    if json_edge['Basic']['label'] == 'on':
        nx.draw_networkx_edge_labels(
            graph,
            pos=nx.get_node_attributes(graph, 'pos'),
        )
    
    # Colorbar
    node_sm = plt.cm.ScalarMappable(cmap=node_cmap, norm=plt.Normalize(vmin=0, vmax=1))
    node_cb = plt.colorbar(node_sm, label='Node', location='left')
    node_cb.set_ticklabels(['0%', '20%', '40%', '60%', '80%', '100%'])
    edge_sm = plt.cm.ScalarMappable(cmap=edge_cmap, norm=plt.Normalize(vmin=0, vmax=1))
    edge_cb = plt.colorbar(edge_sm, label='Link', location='right')
    edge_cb.set_ticklabels(['0%', '20%', '40%', '60%', '80%', '100%'])

    # # Change the color of node boundary
    # ax= plt.gca()
    # ax.collections[0].set_edgecolor("#000000")
    # plt.axis('off')

    plt.savefig(save_as)
    # plt.show()
    plt.close()
