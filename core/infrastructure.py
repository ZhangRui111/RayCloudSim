import math
import networkx as nx
import warnings

from collections import deque
from typing import Optional, Iterator, List

__all__ = ["Location", "Data", "DataFlow", "Node", "Link", "Infrastructure"]


class Location:
    """2d meta location information.

    Attributes:
        x: pos in the x axis.
        y: pos in the y axis.
    """

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"({self.x}, {self.y})"

    def __eq__(self, another):
        return self.x == another.x and self.y == another.y

    def __hash__(self):
        return hash((self.x, self.y))

    def loc(self):
        return self.x, self.y


class Data(object):
    """Data through network links.

    Attributes:
        data_size: size of the data in MB.
    """

    def __init__(self, data_size: float):
        self.data_size = data_size

    def __repr__(self):
        return f"[{self.__class__.__name__}] ({self.data_size})"


class DataFlow(object):
    """Data flow through network links.

    Attributes:
        bit_rate: bit rate of the data flow in Mbps.
        links: all links involved in the path.
    """

    def __init__(self, bit_rate: float):
        self.bit_rate = bit_rate
        self.links: Optional[List["Link"]] = None

    def __repr__(self):
        return f"[{self.__class__.__name__}] ({self.bit_rate})"

    def allocate(self, links: List["Link"]):
        """Allocate the dataflow.

        Place the data flow on a path of links and allocate bandwidth.
        """
        if self.links is not None:
            raise ValueError(f"Cannot place {self} on {links}: It was "
                             f"already placed on path {self.links}.")
        self.links = links
        for link in self.links:
            link.add_data_flow(self)

    def deallocate(self):
        """Deallocate the dataflow.

        Remove the data flow from the infrastructure and deallocate bandwidth.
        """
        if self.links is None:
            raise ValueError(f"{self} is not placed on any links.")
        for link in self.links:
            link.remove_data_flow(self)
        self.links = None


class Node(object):
    """A computing node in the infrastructure graph.

    This can represent any kind of node, e.g.
    - simple sensors without processing capabilities
    - resource constrained nodes fog computing nodes
    - mobile nodes like cars or smartphones
    - entire data centers with virtually unlimited resources

    Attributes:
        node_id: node id, unique in the infrastructure.
        name: node name.
        cu: maximum processing power the node provides in "compute units", an
            imaginary unit for computational power to express differences
            between hardware platforms. If None, the node has unlimited
            processing power.
        used_cu: current occupied cus.
        buffer: FIFO buffer for local-waiting tasks.
        buffer_size: maximum buffer size.
            Note that, once buffer_size > 0, the NoFreeCUsError is replaced by
            the InsufficientBufferError.
        used_buffer: current occupied buffer size.
        location: geographical location.
        power_consumption: power consumption since the simulation begins;
            wired nodes do not need to worry about the current device battery
            level.
        flag_only_wireless: only wireless transmission is allowed.
    """

    def __init__(self, node_id: int, name: str,
                 cu: Optional[float] = None,
                 buffer_size: Optional[int] = 0,
                 location: Optional[Location] = None):
        self.node_id = node_id
        self.name = name
        if cu is None:
            self.cu = math.inf
        else:
            self.cu = cu
        self.used_cu = 0
        self.buffer = deque()  # FIFO deque
        self.buffer_size = buffer_size
        self.used_buffer = 0
        self.location = location

        self.tasks: List["Task"] = []
        self.power_consumption = 0

        self.flag_only_wireless = False

    def __repr__(self):
        return f"{self.name} ({self.used_cu}/{self.cu})".replace('inf', '∞')

    def status(self):
        """User-defined Node status."""
        warnings.warn(
            "deprecated, define it in :class: Scenario instead",
            DeprecationWarning)
        return

    def distance(self, another) -> float:
        """Calculate the Euclidean distance to another node."""
        return math.sqrt(
            (self.location.x - another.location.x) ** 2 +
            (self.location.y - another.location.y) ** 2)

    def utilization(self) -> float:
        """Return the current utilization of the resource."""
        try:
            return self.used_cu / self.cu
        except ZeroDivisionError:
            assert self.used_cu == 0
            return 0.

    def add_task(self, task: "Task"):
        """Add a task to the node."""
        self._reserve_cu(task.cu)
        self.tasks.append(task)

    def remove_task(self, task: "Task"):
        """Remove a task from the node."""
        self._release_cu(task.cu)
        self.tasks.remove(task)

    def buffer_append_task(self, task: "Task"):
        """Append a task to the buffer."""
        if task.task_size_exe <= self.buffer_size - self.used_buffer:
            self.used_buffer += task.task_size_exe
            self.buffer.append(task)
        else:
            raise EnvironmentError(
                ('InsufficientBufferError',
                 f"**InsufficientBufferError: Task {{{task.task_id}}}** "
                 f"insufficient buffer in Node {{{self.name}}}", task.task_id)
            )

    def buffer_pop_task(self):
        """Pop a task from the buffer."""
        if len(self.buffer) > 0:
            task = self.buffer.popleft()
            self.used_buffer -= task.task_size_exe
            return task
        else:
            return None

    def _reserve_cu(self, cu: float):
        new_used_cu = self.used_cu + cu
        if new_used_cu > self.cu:
            raise ValueError(f"Cannot reserve {cu} CU on compute node {self}.")
        self.used_cu = new_used_cu

    def _release_cu(self, cu: float):
        new_used_cu = self.used_cu - cu
        if new_used_cu < 0:
            raise ValueError(f"Cannot release {cu} CU on compute node {self}.")
        self.used_cu = new_used_cu


class Link(object):
    """An unidirectional network link in the infrastructure graph.

    Attributes:
        src: source node.
        dst: destination node.
        bandwidth: bandwidth in Mbps.
        used_bandwidth: used bandwidth in Mbps.
        dis: the distance between its source node and its destination node.
        base_latency: base latency of the network link which can be used to
                      implement routing policies.
        data_flows: store data flows allocated in this network link.
    """

    def __init__(self, src: Node, dst: Node, bandwidth: float,
                 base_latency: Optional[float] = 0):

        if src.flag_only_wireless or dst.flag_only_wireless:
            raise UserWarning(
                "Attempting to create link that links wireless node, which "
                "is not permitted.")

        self.src = src
        self.dst = dst
        self.bandwidth = bandwidth
        self.dis = self.distance()
        self.base_latency = base_latency

        self.used_bandwidth = 0
        self.data_flows: List["DataFlow"] = []

    def __repr__(self):
        return f"{self.src.name} --> {self.dst.name} " \
               f"({self.used_bandwidth}/{self.bandwidth}) ({self.base_latency})"

    def status(self):
        """User-defined Link status."""
        warnings.warn(
            "deprecated, define it in :class: Scenario instead",
            DeprecationWarning)
        return

    def distance(self) -> float:
        """Calculate the Euclidean distance between two nodes
        linked by this link."""
        return math.sqrt(
            (self.src.location.x - self.dst.location.x) ** 2 +
            (self.src.location.y - self.dst.location.y) ** 2)

    def add_data_flow(self, data_flow: DataFlow):
        """Add a data flow to the link and reserve bandwidth."""
        self._reserve_bandwidth(data_flow.bit_rate)
        self.data_flows.append(data_flow)

    def remove_data_flow(self, data_flow: DataFlow):
        """Remove a data flow from the link and release bandwidth."""
        self._release_bandwidth(data_flow.bit_rate)
        self.data_flows.remove(data_flow)

    def _reserve_bandwidth(self, bandwidth):
        new_used_bandwidth = self.used_bandwidth + bandwidth
        if new_used_bandwidth > self.bandwidth:
            raise ValueError(f"Cannot reserve {bandwidth} bandwidth on "
                             f"network link {self}.")
        self.used_bandwidth = new_used_bandwidth

    def _release_bandwidth(self, bandwidth):
        new_used_bandwidth = self.used_bandwidth - bandwidth
        if new_used_bandwidth < 0:
            raise ValueError(f"Cannot release {bandwidth} bandwidth on "
                             f"network link {self}.")
        self.used_bandwidth = new_used_bandwidth


class Infrastructure(object):

    def __init__(self):
        self.graph = nx.MultiDiGraph()

    def add_node(self, node: Node):
        """Add a node to the infrastructure."""
        if node.name not in self.graph:
            self.graph.add_node(node.name, data=node)

    def remove_node(self, name: str):
        """Remove a node from the infrastructure by the node name.

        Removes the node n and all adjacent edges. """
        if name in self.graph:
            self.graph.remove_node(name)

    def add_link(self, link: Link, key=None):
        """Add a link to the infrastructure.

        Missing nodes will be added automatically.

        Args:
            link:
            key: hashable identifier, optional (default=lowest unused integer)
                 Used to distinguish multi-edges between a pair of nodes.
        """
        self.add_node(link.src)
        self.add_node(link.dst)
        # the keyword [dis/latency/*other] is for the weight in
        # get_shortest_path/links
        self.graph.add_edge(link.src.name, link.dst.name, key=key, data=link,
                            dis=link.dis, latency=link.base_latency)

    def remove_link(self, src_name: str, dst_name: str, key=None):
        """Remove a link from the infrastructure by
           src node name and dst node name.

        Users should ensure that the link exists,
        otherwise raise the networkx.exception.NetworkXError.

        Args:
            src_name: name of the source node.
            dst_name: name of the destination node.
            key: hashable identifier, optional (default=lowest unused integer)
                 Used to distinguish multi-edges between a pair of nodes.
        """
        self.graph.remove_edge(src_name, dst_name, key=key)

    def get_node(self, name: str) -> Node:
        """Return a specific node by node name."""
        return self.graph.nodes[name]["data"]

    def get_link(self, src_name: str, dst_name: str, key=0) -> Link:
        """Return a specific link by src node name and dst node name."""
        return self.graph.edges[src_name, dst_name, key]["data"]

    def nodes(self) -> List["Node"]:
        """Return all nodes in the infrastructure."""
        nodes: Iterator[Node] = (v for _, v in self.graph.nodes.data("data"))
        return list(nodes)

    def links(self) -> List["Link"]:
        """Return all links in the infrastructure."""
        links: Iterator[Link] = (v for _, _, v in self.graph.edges.data("data"))
        return list(links)

    def get_shortest_path(self, src_name: str, dst_name: str, weight=None):
        """The shortest path between two nodes.

        Get the shortest path (with given weight) between two nodes.
        """
        shortest_path = nx.shortest_path(self.graph, src_name, dst_name,
                                         weight=weight)
        return shortest_path

    def get_shortest_links(self, src_name: str, dst_name: str, weight=None):
        """The shortest links between two nodes.

        Collect the shortest links (with given weight) between two nodes.
        """
        src, dst = self.get_node(src_name), self.get_node(dst_name)

        shortest_links = []
        if src.flag_only_wireless or dst.flag_only_wireless:
            if src.flag_only_wireless and src.default_dst_node and \
                    dst.flag_only_wireless and dst.default_dst_node:
                shortest_path = nx.shortest_path(self.graph,
                                                 src.default_dst_node.name,
                                                 dst.default_dst_node.name,
                                                 weight=weight)
                shortest_links.append((src_name, src.default_dst_node.name))
                shortest_links += [self.graph.edges[a, b, 0]["data"]
                                   for a, b in nx.utils.pairwise(shortest_path)]
                shortest_links.append((dst.default_dst_node.name, dst_name))
            elif src.flag_only_wireless and src.default_dst_node and \
                not dst.flag_only_wireless:
                shortest_path = nx.shortest_path(self.graph,
                                                 src.default_dst_node.name,
                                                 dst_name,
                                                 weight=weight)
                shortest_links.append((src_name, src.default_dst_node.name))
                shortest_links += [self.graph.edges[a, b, 0]["data"]
                                   for a, b in nx.utils.pairwise(shortest_path)]
            elif not src.flag_only_wireless and \
                    dst.flag_only_wireless and dst.default_dst_node:
                shortest_path = nx.shortest_path(self.graph,
                                                 src_name,
                                                 dst.default_dst_node.name,
                                                 weight=weight)
                shortest_links += [self.graph.edges[a, b, 0]["data"]
                                   for a, b in nx.utils.pairwise(shortest_path)]
                shortest_links.append((dst.default_dst_node.name, dst_name))
            else:
                raise EnvironmentError(
                    ('IsolatedWirelessNode',
                     f"{src_name} or {dst_name} has no accessible wired node.")
                )

            return shortest_links
        else:
            shortest_path = nx.shortest_path(self.graph, src_name, dst_name,
                                             weight=weight)
            shortest_links = [self.graph.edges[a, b, 0]["data"]
                              for a, b in nx.utils.pairwise(shortest_path)]
            return shortest_links

    def get_longest_shortest_path(self):
        """The longest shortest path among all nodes."""
        all_shortest_paths = dict(nx.all_pairs_shortest_path(self.graph))
        res = 0
        for src, val in all_shortest_paths.items():
            for dst, p in val.items():
                res = max(res, len(p) - 1)
        return res
