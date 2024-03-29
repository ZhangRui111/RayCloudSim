from core.base_scenario import BaseScenario
from core.infrastructure import Node, Location

from zoo import WirelessNode, MobileNode


class Scenario(BaseScenario):
    """A simple scenario with 4 wired nodes and 3 wireless node."""

    def init_infrastructure_nodes(self):
        self.node_id2name[0] = 'n0'
        self.node_id2name[1] = 'n1'
        self.node_id2name[2] = 'n2'

        self.infrastructure.add_node(
            Node(node_id=0, name='n0', cu=20, buffer_size=80,
                 location=Location(16, 68)))
        self.infrastructure.add_node(
            Node(node_id=1, name='n1', cu=20, buffer_size=0,
                 location=Location(50, 50)))
        self.infrastructure.add_node(
            Node(node_id=2, name='n2', cu=20, buffer_size=100,
                 location=Location(63, 47)))

    def init_infrastructure_links(self):
        self.add_bilateral_links(self.node_id2name[0],
                                 self.node_id2name[1], 100)
        self.add_bilateral_links(self.node_id2name[1],
                                 self.node_id2name[2], 100)

    def status(self, node_name=None, link_args=None):
        return
