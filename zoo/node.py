import math
import sys

from core.infrastructure import Node, Location

from typing import Optional, List

sys.path.append('..')


class WirelessNode(Node):
    """Wireless Node where data can only be transmitted wirelessly.

    Attributes:
        node_id: node id, unique in the infrastructure.
        name: node name.
        cu: maximum processing power the node provides in "compute units", an
            imaginary unit for computational power to express differences
            between hardware platforms. If None, the node has unlimited
            processing power.
        location: geographical location.
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
                 cu: Optional[float] = None,
                 location: Optional[Location] = None,
                 max_transmit_power: int = 0,
                 radius: float = 100):
        super().__init__(node_id, name, cu, location)

        self.flag_only_wireless = True

        # static attributes
        self.max_transmit_power = max_transmit_power
        self.radius = radius

        # dynamic attributes
        self.transmit_power = 0
        self.access_dst_nodes = []
        self.default_dst_node = None

    def __repr__(self):
        return f"{self.name} ({self.used_cu}/{self.cu} || " \
               f"{self.max_transmit_power})".replace('inf', '∞')

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
        cu: maximum processing power the node provides in "compute units", an
            imaginary unit for computational power to express differences
            between hardware platforms. If None, the node has unlimited
            processing power.
        location: dynamic location, rather than static location.
        max_transmit_power: maximum transmit power.
        radius: wireless accessible range.
        power: current device battery level.
    """

    def __init__(self, node_id: int, name: str,
                 cu: Optional[float] = None,
                 location: Optional[Location] = None,
                 max_transmit_power: int = 0,
                 radius: float = 100,
                 power: float = 100):
        super().__init__(node_id, name, cu, location, max_transmit_power,
                         radius)

        # dynamic attributes
        self.power = power

    def update_location(self, new_loc: Location):
        self.location = new_loc
