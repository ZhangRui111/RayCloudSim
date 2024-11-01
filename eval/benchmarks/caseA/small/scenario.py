import os
import sys

PROJECT_NAME = 'RayCloudSim'
cur_path = os.path.abspath(os.path.dirname(__file__))
root_path = cur_path
while os.path.split(os.path.split(root_path)[0])[-1] != PROJECT_NAME:
    root_path = os.path.split(root_path)[0]
root_path = os.path.split(root_path)[0]
sys.path.append(root_path)

import numpy as np
import pandas as pd

from core.base_scenario import BaseScenario

ROOT_PATH = 'eval/benchmarks/caseA/small'


class Scenario(BaseScenario):
    
    def __init__(self, config_file):
        super().__init__(config_file)
        
        # Load the task dataset
        data = pd.read_csv(f"{ROOT_PATH}/tasks.csv")
        self.simulated_tasks = list(data.iloc[:].values)

    def status(self, node_name=None, link_args=None):
        # Return status of specific Node/Link
        if node_name and link_args:
            node = self.get_node(node_name)
            link = self.get_link(*link_args)
            node_status = [node.max_cpu_freq, node.free_cpu_freq]
            link_statue = [link.max_bandwidth, link.free_bandwidth]
            return node_status, link_statue
        if node_name:
            node = self.get_node(node_name)
            node_status = [node.max_cpu_freq, node.free_cpu_freq]
            return node_status
        if link_args:
            link = self.get_link(*link_args)
            link_statue = [link.max_bandwidth, link.free_bandwidth]
            return link_statue

        # Return status of the whole scenario
        n = len(self.get_nodes())
        node_max_cpu_freq = np.zeros(n)
        node_free_cpu_freq = np.zeros(n)
        link_max_bandwidth = np.zeros((n, n))
        link_free_bandwidth = np.zeros((n, n))

        for _, node in self.get_nodes().items():
            node_max_cpu_freq[node.node_id] = node.max_cpu_freq
            node_free_cpu_freq[node.node_id] = node.free_cpu_freq

        for _, link in self.get_links().items():
            link_max_bandwidth[link.src.node_id][link.dst.node_id] = link.max_bandwidth
            link_free_bandwidth[link.src.node_id][link.dst.node_id] = link.free_bandwidth

        return node_max_cpu_freq, node_free_cpu_freq, link_max_bandwidth, link_free_bandwidth
