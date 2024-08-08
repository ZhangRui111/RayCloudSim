"""Hello World

A toy example.
"""
import os
import sys

current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from core.env import Env
from core.task import Task
from core.vis import *

from examples.scenarios.scenario_1 import Scenario


def main():
    # Create the Env
    scenario=Scenario(config_file="examples/scenarios/configs/config_1.json")
    env = Env(scenario, config_file="core/configs/env_config_null.json")

    # # Visualization: the topology
    # vis_graph(env,
    #           config_file="core/vis/configs/vis_config_base.json", 
    #           save_as="examples/vis/demo_1.png")

    # Begin Simulation
    task = Task(task_id=0,
                task_size=20,
                cycles_per_bit=10,
                trans_bit_rate=20,
                src_name='n0')

    env.process(task=task, dst_name='n1')

    env.run(until=20)  # execute the simulation all at once

    print("\n-----------------------------------------------")
    print("Energy consumption during simulation:\n")
    print(f"n0: {env.node_energy('n0'):.3f}")
    print(f"n1: {env.node_energy('n1'):.3f}")
    print(f"Averaged: {env.avg_node_energy():.3f}")
    print("-----------------------------------------------\n")

    env.close()


if __name__ == '__main__':
    main()


# # ==================== Simulation log ====================
# [0.00]: Task {0} generated in Node {n0}
# [0.00]: Task {0}: {n0} --> {n1}
# [1.00]: Task {0} arrived Node {n1} with {1.00}s
# [1.00]: Processing Task {0} in {n1}
# [11.00]: Task {0} accomplished in Node {n1} with {10.00}s

# -----------------------------------------------
# Energy consumption during simulation:

# n0: 0.200
# n1: 72000.200
# Averaged: 0.036
# -----------------------------------------------

# [20.00]: Simulation completed!
