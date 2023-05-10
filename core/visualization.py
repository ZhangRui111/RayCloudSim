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
        mode='lines')

    node_x = []
    node_y = []
    for node in graph.nodes():
        try:
            x, y = graph.nodes[node]['data'].location.loc()
        except KeyError:
            x, y = graph.nodes[node]['pos']
        node_x.append(x)
        node_y.append(y)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
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
            size=10,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))

    # 2. Color Node Points
    # Color node points by the number of connections.
    # Another option would be to size points by the number of connections,
    # i.e., node_trace.marker.size = node_adjacencies
    node_adjacencies = []
    node_text = []
    for node_id, (adjacencies, node_name) in enumerate(zip(graph.adjacency(),
                                                           graph.nodes())):
        node_adjacencies.append(len(adjacencies[1]))
        try:
            node = graph.nodes[node_name]["data"]
            node_text.append(f"#{node_id} {node.location}")
        except KeyError:
            node_text.append(f"#{node_id} of connections: "
                             f"{len(adjacencies[1])}")

    node_trace.marker.color = node_adjacencies
    # node_trace.marker.size = node_adjacencies  # another option
    node_trace.text = node_text

    # 3. Create Network Graph
    fig = go.Figure(data=[edge_trace, node_trace],
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
