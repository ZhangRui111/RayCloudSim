from core.base_scenario import BaseScenario
from core.node import Node
from core.utils import Location

from zoo import WirelessNode, MobileNode


class Scenario(BaseScenario):
    """A simple scenario with 4 wired nodes and 3 wireless node."""

    def init_infrastructure_nodes(self):

        for node_info in self.json_nodes:

            if node_info['NodeType'] == 'Node':
                self.infrastructure.add_node(
                    Node(
                        id=node_info['NodeId'], 
                        name=node_info['NodeName'], 
                        max_cpu_freq=node_info['MaxCpuFreq'], 
                        max_buffer_size=node_info['MaxBufferSize'], 
                        location=Location(node_info['LocX'], node_info['LocY']),
                        energy_coefficients={
                            'idle': node_info['IdleEnergyCoef'],
                            'exe': node_info['ExeEnergyCoef'],
                        },
                    )
                )
            elif node_info['NodeType'] == 'WirelessNode':
                self.infrastructure.add_node(
                    WirelessNode(
                        id=node_info['NodeId'],
                        name=node_info['NodeName'], 
                        max_cpu_freq=node_info['MaxCpuFreq'], 
                        max_buffer_size=node_info['MaxBufferSize'], 
                        location=Location(node_info['LocX'], node_info['LocY']),
                        energy_coefficients={
                            'idle': node_info['IdleEnergyCoef'],
                            'exe': node_info['ExeEnergyCoef'],
                        },
                        max_transmit_power=node_info['MaxTransmitPower'], 
                        radius=node_info['Radius'],
                    )
                )
            elif node_info['NodeType'] == 'MobileNode':
                self.infrastructure.add_node(
                    MobileNode(
                        id=node_info['NodeId'],
                        name=node_info['NodeName'], 
                        max_cpu_freq=node_info['MaxCpuFreq'], 
                        max_buffer_size=node_info['MaxBufferSize'], 
                        location=Location(node_info['LocX'], node_info['LocY']),
                        energy_coefficients={
                            'idle': node_info['IdleEnergyCoef'],
                            'exe': node_info['ExeEnergyCoef'],
                        },
                        max_transmit_power=node_info['MaxTransmitPower'], 
                        radius=node_info['Radius'], 
                        power=node_info['Power'],
                    )
                )

            self.node_id2name[node_info['NodeId']] = node_info['NodeName']

    def status(self, node_name=None, link_args=None):
        return
