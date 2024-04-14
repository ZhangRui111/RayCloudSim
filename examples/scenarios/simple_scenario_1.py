from core.base_scenario import BaseScenario
from core.infrastructure import Node, Location


class Scenario(BaseScenario):
    """A simple scenario with 2 nodes and 1 bilateral link."""

    def init_infrastructure_nodes(self):
        self.node_id2name[0] = 'n0'
        self.node_id2name[1] = 'n1'

        self.infrastructure.add_node(
            Node(node_id=0, name='n0', max_cpu_freq=20, max_buffer_size=100,
                 location=Location(16, 68)))
        self.infrastructure.add_node(
            Node(node_id=1, name='n1', max_cpu_freq=20, max_buffer_size=100,
                 location=Location(63, 47)))

    def init_infrastructure_links(self):
        self.add_bilateral_links(self.node_id2name[0],
                                 self.node_id2name[1], [100, 90])

    def status(self, node_name=None, link_args=None):
        return
