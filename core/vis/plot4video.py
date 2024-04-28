import cv2
import glob
import json
import networkx as nx
import matplotlib as mpl
import matplotlib.pyplot as plt
import os
from tqdm import tqdm


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
    
    plt.figure(figsize=(10, 8))
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
        alpha=json_edge['Basic']['alpha'],
    )

    if json_edge['Basic']['label'] == 'on':
        nx.draw_networkx_edge_labels(
            graph,
            pos=nx.get_node_attributes(graph, 'pos'),
        )
    
    # Colorbar
    node_sm = plt.cm.ScalarMappable(cmap=node_cmap, norm=plt.Normalize(vmin=0, vmax=1))
    node_cb = plt.colorbar(node_sm, label='Node', location='left', format=lambda x, _: f"{x:.0%}")
    edge_sm = plt.cm.ScalarMappable(cmap=edge_cmap, norm=plt.Normalize(vmin=0, vmax=1))
    edge_cb = plt.colorbar(edge_sm, label='Link', location='right', format=lambda x, _: f"{x:.0%}")

    # # Change the color of node boundary
    # ax= plt.gca()
    # ax.collections[0].set_edgecolor("#000000")
    # plt.axis('off')

    plt.savefig(save_as)
    # plt.show()
    plt.close()


def frame2video(img_path, video_save_as):
    img_array = []
    files = glob.glob(f"{img_path}/*.png")
    files.sort(key=os.path.getmtime)  # sort all images in time order.
    for filename in tqdm(files):
        img = cv2.imread(filename)
        height, width, layers = img.shape
        size = (width, height)
        img_array.append(img)
    
    out = cv2.VideoWriter(video_save_as, 
                          cv2.VideoWriter_fourcc(*'DIVX'), 
                          fps=5, 
                          frameSize=size)
    
    for i in range(len(img_array)):
        out.write(img_array[i])
    
    out.release()


def vis_frame2video(env):
    """Build the simulation video, based on the simulation logs."""
    frame_save_path = f"{env.config['Log']['LogFramesPath']}"
    if len(os.listdir(frame_save_path)) == 0:
        with open(f"{env.config['Log']['LogInfoPath']}/info4frame.json", 'r') as fr:
            info4frame = json.load(fr)
        for k, v in tqdm(info4frame.items()):
            v['now'] = k
            plot_frame(env.scenario.infrastructure.graph,
                        v, 
                        config_file="core/vis/configs/vis_config_4video.json", 
                        save_as=f"{frame_save_path}/frame_{k}.png")
    
    frame2video(frame_save_path, f"{env.config['Log']['LogInfoPath']}/out.avi")
