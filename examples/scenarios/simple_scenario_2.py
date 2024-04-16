from core.base_scenario import BaseScenario
from core.infrastructure import Node, Location

from zoo import WirelessNode, MobileNode


class Scenario(BaseScenario):
    """A simple scenario with 4 wired nodes and 3 wireless node."""

    def init_infrastructure_nodes(self):
        self.node_id2name[0] = 'n0'
        self.node_id2name[1] = 'n1'
        self.node_id2name[2] = 'n2'
        self.node_id2name[3] = 'n3'
        self.node_id2name[4] = 'n4'
        self.node_id2name[5] = 'n5'
        self.node_id2name[6] = 'n6'

        self.infrastructure.add_node(
            Node(node_id=0, name='n0', 
                 max_cpu_freq=20, max_buffer_size=100,
                 location=Location(16, 68), 
                 idle_energy_coef=0.01, exe_energy_coef=1))
        self.infrastructure.add_node(
            Node(node_id=1, name='n1', 
                 max_cpu_freq=20, max_buffer_size=100,
                 location=Location(50, 50), 
                 idle_energy_coef=0.01, exe_energy_coef=1))
        self.infrastructure.add_node(
            Node(node_id=2, name='n2', 
                 max_cpu_freq=20, max_buffer_size=100,
                 location=Location(63, 47), 
                 idle_energy_coef=0.01, exe_energy_coef=1))
        self.infrastructure.add_node(
            Node(node_id=3, name='n3', 
                 max_cpu_freq=20, max_buffer_size=100,
                 location=Location(58, 45), 
                 idle_energy_coef=0.01, exe_energy_coef=1))
        self.infrastructure.add_node(
            WirelessNode(node_id=4, name='n4', 
                         max_cpu_freq=20, max_buffer_size=100,
                         location=Location(14, 64), 
                         idle_energy_coef=0.01, exe_energy_coef=0.1,
                         max_transmit_power=10, radius=10))
        self.infrastructure.add_node(
            MobileNode(node_id=5, name='n5', 
                       max_cpu_freq=20, max_buffer_size=100,
                       location=Location(60, 44), 
                       idle_energy_coef=0.01, exe_energy_coef=0.1,
                       max_transmit_power=10, radius=10, power=10))
        self.infrastructure.add_node(
            WirelessNode(node_id=6, name='n6', 
                         max_cpu_freq=20, max_buffer_size=100,
                         location=Location(30, 40),
                         idle_energy_coef=0.01, exe_energy_coef=0.1,
                         max_transmit_power=10, radius=10))

    def init_infrastructure_links(self):
        self.add_bilateral_links(self.node_id2name[0],
                                 self.node_id2name[1], 100)
        self.add_bilateral_links(self.node_id2name[1],
                                 self.node_id2name[2], 100)
        self.add_bilateral_links(self.node_id2name[2],
                                 self.node_id2name[3], 100)

    def status(self, node_name=None, link_args=None):
        return
