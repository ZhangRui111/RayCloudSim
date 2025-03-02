import math
import networkx as nx
import warnings

from collections import deque, namedtuple
from typing import Optional, Iterator, List, Dict

__all__ = ["Location", "Data", "DataFlow", "Buffer", "Node", "Link", "Infrastructure"]

# Named tuples for buffer and CPU status
BufferStatus = namedtuple("BufferStatus", "free_size, max_size")
CPUStatus = namedtuple("CPUStatus", "free_cpu_freq, max_cpu_freq")


class Location:
    """2D location information for nodes.

    Attributes:
        x (float): The x-coordinate.
        y (float): The y-coordinate.
    """

    def __init__(self, x: float, y: float):
        """Initialize Location object with x and y coordinates."""
        self.x = x
        self.y = y

    def __repr__(self):
        """Return a string representation of the location."""
        return f"({self.x}, {self.y})"

    def __eq__(self, another):
        """Check equality with another Location object."""
        return self.x == another.x and self.y == another.y

    def __hash__(self):
        """Return the hash value for the location."""
        return hash((self.x, self.y))

    def loc(self):
        """Return the (x, y) coordinates."""
        return self.x, self.y


class Data(object):
    """Represents data transferred through network links.

    Attributes:
        data_size (float): Size of the data in bits.
    """

    def __init__(self, data_size: float):
        """Initialize Data object with a specified data size."""
        self.data_size = data_size

    def __repr__(self):
        """Return a string representation of the data."""
        return f"[{self.__class__.__name__}] ({self.data_size})"


class DataFlow(object):
    """Represents a data flow through network links.

    Attributes:
        bit_rate (float): The bit rate of the data flow in bps.
        links (Optional[List[Link]]): The list of links involved in the data flow path.
    """

    def __init__(self, bit_rate: float):
        """Initialize DataFlow with a specified bit rate."""
        self.bit_rate = bit_rate
        self.links: Optional[List["Link"]] = None

    def __repr__(self):
        """Return a string representation of the data flow."""
        return f"[{self.__class__.__name__}] ({self.bit_rate})"

    def allocate(self, links: List["Link"]):
        """Allocate the data flow to a list of links."""
        if self.links is not None:
            raise ValueError(f"Cannot place {self} on {links}: It is already placed on path {self.links}.")

        self.links = links
        for link in self.links:
            link.add_data_flow(self)

    def deallocate(self):
        """Deallocate the data flow from the infrastructure."""
        if self.links is None:
            raise ValueError(f"{self} is not placed on any links.")
        for link in self.links:
            link.remove_data_flow(self)
        self.links = None


class Buffer(object):
    """FIFO buffer for task management.

    Attributes:
        max_size (int): The maximum buffer size.
        free_size (int): The current available buffer size.
    """

    def __init__(self, max_size):
        """Initialize a FIFO buffer with a specified maximum size."""
        self.buffer = deque()  # FIFO queue
        self.task_ids = []  # List of task IDs
        self.max_size = max_size
        self.free_size = max_size

    def append(self, task: "Task"):
        """Append a task to the buffer if enough space is available."""
        if task.task_size <= self.free_size:
            self.free_size -= task.task_size
            self.buffer.append(task)
            self.task_ids.append(task.task_id)
        else:
            raise EnvironmentError(
                ('InsufficientBufferError', 
                 f"**InsufficientBufferError: Task {{{task.task_id}}}** "
                 f"insufficient buffer in Node {{{task.dst.name}}}", task.task_id))

    def pop(self) -> Optional["Task"]:
        """Pop the first task from the buffer."""
        if self.buffer:
            task = self.buffer.popleft()
            self.task_ids.remove(task.task_id)
            self.free_size += task.task_size
            return task
        return None
    
    def utilization(self) -> BufferStatus:
        """Return the current buffer utilization."""
        return BufferStatus(self.free_size, self.max_size)
    
    def reset(self):
        """Reset the buffer to its initial state."""
        self.buffer.clear()
        self.task_ids.clear()
        self.free_size = self.max_size


class Node(object):
    """
    A computing node in the infrastructure graph.

    This class can represent different types of nodes, such as:
      - Simple sensors without processing capabilities
      - Resource-constrained fog computing nodes
      - Mobile nodes like cars or smartphones
      - Entire data centers with virtually unlimited resources

    Attributes:
        node_id: The unique node identifier.
        name: The name of the node.
        max_cpu_freq: The maximum CPU frequency of the node.
        free_cpu_freq: The current available CPU frequency.
            Note: At present, free_cpu_freq can be '0' or 'max_cpu_freq', i.e., one task at a time.
        task_buffer: FIFO buffer for queued tasks.
            Note: The buffer is not used for executing tasks; 
            tasks can be executed even when the buffer is zero.
        location: The geographical location of the node.
        idle_energy_coef: Energy consumption coefficient during idle state.
        exe_energy_coef: Energy consumption coefficient during working/computing state.
        active_tasks: List of active tasks on the node.
        energy_consumption: The total energy consumption..
        flag_only_wireless: Whether the node only supports wireless transmission.
    """

    def __init__(self, node_id: int, name: str, max_cpu_freq: float, 
                 max_buffer_size: Optional[int] = 0, location: Optional[Location] = None,
                 idle_energy_coef: Optional[float] = 0, exe_energy_coef: Optional[float] = 0):
        # Initialize node attributes
        self.node_id = node_id
        self.name = name
        self.max_cpu_freq = max_cpu_freq
        self.free_cpu_freq = max_cpu_freq

        # Buffer for tasks
        self.task_buffer = Buffer(max_buffer_size)

        # Location and energy coefficients
        self.location = location
        self.energy_consumption = 0
        self.idle_energy_coef = idle_energy_coef
        self.exe_energy_coef = exe_energy_coef
        
        # Track active tasks and task IDs
        self.active_tasks: List["Task"] = []
        self.active_task_ids = []

        # Wireless flag and other system variables
        self.flag_only_wireless = False
        self.total_cpu_freq = 0
        self.clock = 0

    def __repr__(self):
        """Returns a string representation of the node."""
        return f"{self.name} ({self.free_cpu_freq}/{self.max_cpu_freq})"

    def buffer_free_size(self, val=None):
        """Obtain or modify the buffer's free size."""
        if val is None:
            return self.task_buffer.free_size
        else:
            self.task_buffer.free_size += val
    
    def append_task(self, task: "Task"):
        """Append a task to the task buffer."""
        self.task_buffer.append(task)

    def pop_task(self):
        """Pop a task from the task buffer."""
        return self.task_buffer.pop()

    def status(self):
        """Deprecated: Use the :class: Scenario for defining node status."""
        warnings.warn("deprecated, define it in :class: Scenario instead", DeprecationWarning)

    def distance(self, another, type='euclidean') -> float:
        """Calculate the distance between this node and another node."""
        if type == 'haversine':
            return self.haversine(self.location.x, self.location.y, 
                                  another.location.x, another.location.y)
        elif type == 'euclidean':
            return self.euclidean_distance(another)
        else:
            raise ValueError(f"Unsupported distance type: {type}")
        
    def haversine(self, lat1, lon1, lat2, lon2) -> float:
        """
        Calculate the Haversine distance (great-circle distance) between two points on Earth.

        Parameters:
            lat1, lon1: Latitude and longitude of point 1 (in decimal degrees)
            lat2, lon2: Latitude and longitude of point 2 (in decimal degrees)

        Returns:
            Distance in kilometers.
        """
        # Convert decimal degrees to radians.
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

        # Compute differences.
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        # Haversine formula.
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        # Radius of Earth in kilometers (6371000 for meters)
        R = 6371000
        distance = R * c
        return distance

    def euclidean_distance(self, another) -> float:
        """Calculate the Euclidean distance between this node and another node."""
        return math.sqrt(
            (self.location.x - another.location.x) ** 2 +
            (self.location.y - another.location.y) ** 2
        )

    def utilization(self):
        """Returns CPU and buffer utilization."""
        return CPUStatus(self.free_cpu_freq, self.max_cpu_freq), self.task_buffer.utilization()
    
    def quantify_cpu_freq(self):
        """Returns the ratio of used CPU frequency to the maximum CPU frequency."""
        return (self.max_cpu_freq - self.free_cpu_freq) / self.max_cpu_freq

    def quantify_buffer_size(self):
        """Returns the ratio of used buffer size to the maximum buffer size."""
        return (self.task_buffer.max_size - self.task_buffer.free_size) / self.task_buffer.max_size

    def add_task(self, task: "Task"):
        """Add a task to the node."""
        self._reserve_resource(task)
        self.active_tasks.append(task)
        self.active_task_ids.append(task.task_id)

    def remove_task(self, task: "Task"):
        """Remove a task from the node."""
        self._release_resource(task)
        self.active_tasks.remove(task)
        self.active_task_ids.remove(task.task_id)

    def _reserve_resource(self, task: "Task"):
        """Reserve CPU resources for the task."""
        if self.free_cpu_freq > 0:
            task.cpu_freq = self.free_cpu_freq
            self.free_cpu_freq = 0
        else:
            raise ValueError(f"Cannot reserve enough resources on compute node {self}.")

    def _release_resource(self, task: "Task"):
        """Release CPU resources from the task."""
        if self.free_cpu_freq == 0:
            self.free_cpu_freq = self.max_cpu_freq
        else:
            raise ValueError(f"Cannot release enough resources on compute node {self}.")
    
    def reset(self):
        """Reset the node to its initial state."""
        self.free_cpu_freq = self.max_cpu_freq
        self.task_buffer.reset()
        self.energy_consumption = 0
        self.active_tasks.clear()
        self.active_task_ids.clear()


class Link(object):
    """An unidirectional network link in the infrastructure graph.

    Attributes:
        src: Source node of the link.
        dst: Destination node of the link.
        max_bandwidth: Maximum bandwidth in bps.
        free_bandwidth: Current available bandwidth in bps.
        dis: Distance between the source node and the destination node.
        base_latency: Base latency of the link, useful for routing policies.
        data_flows: List of data flows allocated on this link.
    """

    def __init__(self, src: Node, dst: Node, max_bandwidth: float, base_latency: Optional[float] = 0):
        """Initializes a network link with source and destination nodes."""
        # Check if either node is wireless, which is not allowed for links.
        if src.flag_only_wireless or dst.flag_only_wireless:
            raise UserWarning("Attempting to create a link between wireless nodes is not permitted.")

        self.src = src
        self.dst = dst
        self.max_bandwidth = max_bandwidth
        self.base_latency = base_latency
        try:
            self.dis = self._calculate_distance()
        except AttributeError:
            self.dis = 1
        self.free_bandwidth = max_bandwidth
        self.data_flows: List["DataFlow"] = []

    def __repr__(self):
        """Returns a string representation of the link."""
        return f"{self.src.name} --> {self.dst.name} ({self.free_bandwidth}/{self.max_bandwidth}) ({self.base_latency})"

    def status(self):
        """User-defined Link status (deprecated)."""
        warnings.warn("Deprecated. Define it in :class: Scenario instead.", DeprecationWarning)

    def _calculate_distance(self) -> float:
        """Calculate and return the Euclidean distance between the source and destination nodes."""
        return math.sqrt(
            (self.src.location.x - self.dst.location.x) ** 2 +
            (self.src.location.y - self.dst.location.y) ** 2
        )

    def add_data_flow(self, data_flow: DataFlow):
        """Add a data flow to the link and reserve bandwidth."""
        self._reserve_bandwidth(data_flow.bit_rate)
        self.data_flows.append(data_flow)

    def remove_data_flow(self, data_flow: DataFlow):
        """Remove a data flow from the link and release bandwidth."""
        self._release_bandwidth(data_flow.bit_rate)
        self.data_flows.remove(data_flow)

    def _reserve_bandwidth(self, bandwidth: float):
        """Reserves bandwidth for a data flow."""
        if self.free_bandwidth < bandwidth:
            raise ValueError(f"Cannot reserve {bandwidth} bandwidth on link {self}. Not enough free bandwidth.")
        self.free_bandwidth -= bandwidth

    def _release_bandwidth(self, bandwidth: float):
        """Releases bandwidth after removing a data flow."""
        if self.free_bandwidth + bandwidth > self.max_bandwidth:
            raise ValueError(f"Cannot release {bandwidth} bandwidth on link {self}. Exceeds max bandwidth.")
        self.free_bandwidth += bandwidth
    
    def quantify_bandwidth(self) -> float:
        """Returns the ratio of used bandwidth to the maximum bandwidth."""
        return (self.max_bandwidth - self.free_bandwidth) / self.max_bandwidth

    def reset(self):
        """Resets the link's bandwidth to its maximum and clears the data flows."""
        self.free_bandwidth = self.max_bandwidth
        self.data_flows.clear()


class Infrastructure(object):
    """Class representing the infrastructure network with nodes and links.

    This class allows you to manage the infrastructure graph by adding/removing
    nodes and links, as well as retrieving paths, nodes, and links with various
    attributes.
    """

    def __init__(self):
        """Initializes the infrastructure with an empty directed graph."""
        self.graph = nx.MultiDiGraph()

    def add_node(self, node: Node):
        """Add a node to the infrastructure.

        If the node does not exist, it will be added to the graph with its position
        if available.
        """
        if node.name not in self.graph:
            node_data = {'data': node}
            if node.location:
                node_data['pos'] = list(node.location.loc())
            self.graph.add_node(node.name, **node_data)

    def remove_node(self, name: str):
        """Remove a node and all its adjacent edges from the infrastructure by node name."""
        if name in self.graph:
            self.graph.remove_node(name)

    def add_link(self, link: Link, key=None):
        """Add a link between two nodes, automatically adding nodes if missing.

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
        """Remove a specific link between two nodes identified by their names.

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
        """Retrieve a specific node by its name."""
        return self.graph.nodes[name]["data"]

    def get_link(self, src_name: str, dst_name: str, key=0) -> Link:
        """Retrieve a specific link by the source and destination node names."""
        return self.graph.edges[src_name, dst_name, key]["data"]

    def get_nodes(self) -> Dict[str, Node]:
        """Retrieve all nodes in the infrastructure as a dictionary of node names to nodes."""
        # # v1: return as a list
        # nodes: Iterator[Node] = (v for _, v in self.graph.nodes.data("data"))
        # return list(nodes)
        # --------------------
        # v2: return as a dict
        return dict(nx.get_node_attributes(self.graph, 'data'))

    def get_links(self) -> Dict[str, Link]:
        """Retrieve all links in the infrastructure as a dictionary of edge keys to links."""
        # # v1: return as a list
        # links: Iterator[Link] = (v for _, _, v in self.graph.edges.data("data"))
        # return list(links)
        # --------------------
        # v2: return as a dict
        return nx.get_edge_attributes(self.graph, 'data')

    def get_shortest_path(self, src_name: str, dst_name: str, weight=None):
        """Retrieve the shortest path between two nodes based on the provided weight."""
        return nx.shortest_path(self.graph, src_name, dst_name, weight=weight)

    def get_shortest_links(self, src_name: str, dst_name: str, weight: Optional[str] = None):
        """Retrieve the shortest links between two nodes, considering specific routing rules."""
        src, dst = self.get_node(src_name), self.get_node(dst_name)

        if src.flag_only_wireless or dst.flag_only_wireless:
            return self._get_shortest_wireless_links(src, dst, weight)
        else:
            return self._get_standard_shortest_links(src_name, dst_name, weight)

    def _get_shortest_wireless_links(self, src: Node, dst: Node, weight: Optional[str] = None):
        """Handle the case where one or both nodes are wireless."""
        shortest_links = []

        if src.flag_only_wireless and src.default_dst_node and \
           dst.flag_only_wireless and dst.default_dst_node:
            shortest_path = nx.shortest_path(self.graph,
                                             src.default_dst_node.name,
                                             dst.default_dst_node.name,
                                             weight=weight)
            shortest_links.append((src.name, src.default_dst_node.name))
            shortest_links += [self.graph.edges[a, b, 0]["data"]
                               for a, b in nx.utils.pairwise(shortest_path)]
            shortest_links.append((dst.default_dst_node.name, dst.name))
        elif src.flag_only_wireless and src.default_dst_node:
            shortest_path = nx.shortest_path(self.graph,
                                             src.default_dst_node.name,
                                             dst.name,
                                             weight=weight)
            shortest_links.append((src.name, src.default_dst_node.name))
            shortest_links += [self.graph.edges[a, b, 0]["data"]
                               for a, b in nx.utils.pairwise(shortest_path)]
        elif dst.flag_only_wireless and dst.default_dst_node:
            shortest_path = nx.shortest_path(self.graph,
                                             src.name,
                                             dst.default_dst_node.name,
                                             weight=weight)
            shortest_links += [self.graph.edges[a, b, 0]["data"]
                               for a, b in nx.utils.pairwise(shortest_path)]
            shortest_links.append((dst.default_dst_node.name, dst.name))
        else:
            raise EnvironmentError(
                ('IsolatedWirelessNode', f"{src.name} or {dst.name} has no accessible wired node.")
            )

        return shortest_links

    def _get_standard_shortest_links(self, src_name: str, dst_name: str, weight: Optional[str] = None):
        """Retrieve the standard shortest links between two nodes."""
        shortest_path = nx.shortest_path(self.graph, src_name, dst_name, weight=weight)
        return [self.graph.edges[a, b, 0]["data"]
                for a, b in nx.utils.pairwise(shortest_path)]

    def get_longest_shortest_path(self) -> int:
        """Return the longest shortest path length among all pairs of nodes in the infrastructure."""
        all_shortest_paths = dict(nx.all_pairs_shortest_path(self.graph))
        return max(len(p) - 1 for val in all_shortest_paths.values() for p in val.values())