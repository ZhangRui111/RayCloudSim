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

ROOT_PATH = 'eval/benchmarks/Topo4MEC/data'


class Scenario(BaseScenario):
    
    def __init__(self, config_file, flag):
        """
        :param flag: '25N50E', '50N50E', '100N150E' or 'MilanCityCenter'
        """
        assert flag in ['25N50E', '50N50E', '100N150E', 'MilanCityCenter'], f"Invalid flag={flag}"
        super().__init__(config_file)
        
        # Load the task dataset
        data = pd.read_csv(f"{ROOT_PATH}/{flag}/tasks.csv")
        self.simulated_tasks = list(data.iloc[:].values)
    
    def status(self):
        pass
