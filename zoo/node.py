import os
import sys

PROJECT_NAME = 'RayCloudSim'
cur_path = os.path.abspath(os.path.dirname(__file__))
root_path = cur_path
while os.path.split(os.path.split(root_path)[0])[-1] != PROJECT_NAME:
    root_path = os.path.split(root_path)[0]
root_path = os.path.split(root_path)[0]
sys.path.append(root_path)

import math

from typing import Optional, List

from core.infrastructure import Node, Location


class WirelessNode(Node):
    """Wireless Node where data can only be transmitted wirelessly.

    Attributes:
        node_id: node id, unique in the infrastructure.
        name: node name.
        max_cpu_freq: maximum cpu frequency.
        free_cpu_freq: current available cpu frequency.
            Note: At present, free_cpu_freq can be '0' or 'max_cpu_freq', i.e., one task at a time.
        task_buffer: FIFO buffer for local-waiting tasks.
            Note: The buffer is not used for executing tasks; 
            tasks can be executed even when the buffer is zero.
        location: geographical location.
        tasks: tasks placed in the node.
        power_consumption: power consumption since the simulation begins;
            wired nodes do not need to worry about the current device battery level.
        flag_only_wireless: only wireless transmission is allowed.
        max_transmit_power: maximum transmit power.
        transmit_power: transmit power for one data transmission, which is
            necessary for modeling the SINR, SNR, etc.
        radius: wireless accessible range.
        access_dst_nodes: all wireless-accessible nodes, including
            wired/wireless nodes.
        default_dst_node: default (usually the closest) wired node for
            multi-hop communication.
    """
    def __init__(self, node_id: int, name: str,
                 max_cpu_freq: float = None,
                 max_buffer_size: Optional[int] = 0,
                 location: Optional[Location] = None,
                 max_transmit_power: int = 0,
                 radius: float = 100):
        super().__init__(node_id, name, max_cpu_freq, max_buffer_size, location)

        self.flag_only_wireless = True

        # static attributes
        self.max_transmit_power = max_transmit_power
        self.radius = radius

        # dynamic attributes
        self.transmit_power = 0
        self.access_dst_nodes = []
        self.default_dst_node = None

    def __repr__(self):
        return f"{self.name} ({self.free_cpu_freq}/{self.max_cpu_freq}) || " \
               f"{self.max_transmit_power})"

    def update_access_dst_nodes(self, nodes: List[Node]):
        """Update the current wireless-accessible nodes."""
        del self.access_dst_nodes[:]
        self.default_dst_node = None

        wired_dis = math.inf
        for item in nodes:
            if item.node_id != self.node_id:
                dis = self.distance(item)
                if dis < self.radius:
                    self.access_dst_nodes.append(item)
                    if not item.flag_only_wireless and dis < wired_dis:
                        self.default_dst_node = item
                        wired_dis = dis


class MobileNode(WirelessNode):
    """Mobile Node.

    (1) data can only be transmitted wirelessly.
    (2) dynamic location instead of static location.

    Attributes:
        node_id: node id, unique in the infrastructure.
        name: node name.
        max_cpu_freq: maximum cpu frequency.
        free_cpu_freq: current available cpu frequency.
            Note: At present, free_cpu_freq can be '0' or 'max_cpu_freq', i.e., one task at a time.
        task_buffer: FIFO buffer for local-waiting tasks.
            Note: The buffer is not used for executing tasks; 
            tasks can be executed even when the buffer is zero.
        location: geographical location.
        tasks: tasks placed in the node.
        power_consumption: power consumption since the simulation begins;
            wired nodes do not need to worry about the current device battery level.
        flag_only_wireless: only wireless transmission is allowed.
        max_transmit_power: maximum transmit power.
        radius: wireless accessible range.
        power: current device battery level.
    """

    def __init__(self, node_id: int, name: str,
                 max_cpu_freq: float = None,
                 max_buffer_size: Optional[int] = 0,
                 location: Optional[Location] = None,
                 max_transmit_power: int = 0,
                 radius: float = 100,
                 power: float = 100):
        super().__init__(node_id, name, max_cpu_freq, max_buffer_size, location,
                         max_transmit_power, radius)

        # dynamic attributes
        self.power = power

    def update_location(self, new_loc: Location):
        self.location = new_loc
