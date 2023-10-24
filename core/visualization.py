import networkx as nx
import os

from plotly import graph_objs as go


def plot_2d_network_graph(graph: nx.Graph, save_as: str = None):
    """Visualization a networkx graph."""
    # 1. Create Edges
    # Add edges as disconnected lines in a single trace and
    # nodes as a scatter trace
    edge_x = []
    edge_y = []
    for edge in graph.edges():
        try:
            x0, y0 = graph.nodes[edge[0]]['data'].location.loc()
        except KeyError:
            x0, y0 = graph.nodes[edge[0]]['pos']
        try:
            x1, y1 = graph.nodes[edge[1]]['data'].location.loc()
        except KeyError:
            x1, y1 = graph.nodes[edge[1]]['pos']
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines',
    )

    wired_node_x, wired_node_y = [], []
    wireless_node_x, wireless_node_y = [], []
    for node in graph.nodes():
        try:
            node_data = graph.nodes[node]['data']
            x, y = node_data.location.loc()
            flag_only_wireless = node_data.flag_only_wireless
            if flag_only_wireless:
                wireless_node_x.append(x)
                wireless_node_y.append(y)
            else:
                wired_node_x.append(x)
                wired_node_y.append(y)
        except KeyError:
            x, y = graph.nodes[node]['pos']
            wired_node_x.append(x)
            wired_node_y.append(y)

    wired_node_trace = go.Scatter(
        x=wired_node_x, y=wired_node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            # colorscale options
            # 'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
            # 'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
            # 'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
            colorscale='YlGnBu',
            reversescale=True,
            color=[],
            size=14,
            symbol='circle',
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),
            line_width=2,
        )
    )
    wireless_node_trace = go.Scatter(
        x=wireless_node_x, y=wireless_node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            reversescale=True,
            color='black',
            size=10,
            symbol='star-diamond',
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),
            line_width=2,
        )
    )

    # 2. Color Node Points
    # Color node points by the number of connections.
    # Another option would be to size points by the number of connections,
    # i.e., node_trace.marker.size = node_adjacencies
    wired_node_adjacencies = []
    wired_node_text, wireless_node_text = [], []
    for node_id, (adjacencies, node_name) in enumerate(zip(graph.adjacency(),
                                                           graph.nodes())):
        wired_node_adjacencies.append(len(adjacencies[1]))
        try:
            node_data = graph.nodes[node_name]['data']
            if node_data.flag_only_wireless:
                wireless_node_text.append(f"#{node_id} (wireless) "
                                          f"{node_data.location}")
            else:
                wired_node_text.append(f"#{node_id} {node_data.location}")
        except KeyError:
            wired_node_text.append(f"#{node_id} of connections: "
                             f"{len(adjacencies[1])}")

    wired_node_trace.marker.color = wired_node_adjacencies
    # node_trace.marker.size = wired_node_adjacencies  # another option
    wired_node_trace.text = wired_node_text
    wireless_node_trace.text = wireless_node_text

    # 3. Create Network Graph
    fig = go.Figure(data=[edge_trace, wired_node_trace, wireless_node_trace],
                    layout=go.Layout(
                        title="Network Graph Visualization",
                        showlegend=False,
                        hovermode='closest',
                        autosize=False,
                        width=800,
                        height=800,
                        margin=dict(b=20, l=5, r=5, t=40),
                        annotations=[dict(
                            text="network",
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0.005, y=-0.002)],
                        xaxis=dict(showgrid=False, zeroline=False,
                                   showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False,
                                   showticklabels=False))
                    )

    # 4. Saving and Visualizing
    if save_as:
        os.makedirs(os.path.dirname(save_as), exist_ok=True)
        fig.write_image(save_as, engine='auto')

    fig.show()


def main():
    # example
    graph = nx.random_geometric_graph(n=50, radius=0.25, dim=2, pos=None,
                                      p=2, seed=5)
    plot_2d_network_graph(graph)


if __name__ == '__main__':
    main()
