"""Example

Example on simulation that considers the wireless transmission.
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

from examples.scenarios.scenario_5 import Scenario


def main():
    # Create the Env
    scenario=Scenario(config_file="examples/scenarios/configs/config_5.json")
    env = Env(scenario, config_file="core/configs/env_config_null.json")

    # # Visualization: the topology
    # vis_graph(env,
    #           config_file="core/vis/configs/vis_config_base.json", 
    #           save_as="examples/vis/demo_5.png")

    # Begin Simulation
    task0 = Task(task_id=0,
                 task_size=20,
                 cycles_per_bit=1,
                 trans_bit_rate=20,
                 src_name='n4')

    env.process(task=task0, dst_name='n5')
    # routing path: [('n4', 'n0'), n0 --> n1, n1 --> n2, n2 --> n3, ('n3', 'n5')]

    env.run(until=10)  # execute the simulation until 10

    task1 = Task(task_id=1,
                 task_size=20,
                 cycles_per_bit=1,
                 trans_bit_rate=20,
                 src_name='n1')

    env.process(task=task1, dst_name='n5')

    env.run(until=20)  # execute the simulation from 10 to 20
    # routing path: [n1 --> n2, n2 --> n3, ('n3', 'n5')]

    print("\n-----------------------------------------------")
    print("Energy consumption during simulation:\n")
    for key in env.scenario.get_nodes().keys():
        print(f"{key}: {env.node_energy(key):.3f}")
    print(f"Averaged: {env.avg_node_energy():.3f}")
    print("-----------------------------------------------\n")

    env.close()


if __name__ == '__main__':
    main()


# # ==================== Simulation log ====================
# [0.00]: Task {0} generated in Node {n4}
# [0.00]: Task {0}: {n4} --> {n5}
# [3.00]: Task {0} arrived Node {n5} with {3.00}s
# [3.00]: Processing Task {0} in {n5}
# [4.00]: Task {0} accomplished in Node {n5} with {1.00}s
# [10.00]: Task {1} generated in Node {n1}
# [10.00]: Task {1}: {n1} --> {n5}
# [12.00]: Task {1} arrived Node {n5} with {2.00}s
# [12.00]: Processing Task {1} in {n5}
# [13.00]: Task {1} accomplished in Node {n5} with {1.00}s

# -----------------------------------------------
# Energy consumption during simulation:

# n0: 0.000
# n1: 0.000
# n2: 0.000
# n3: 0.000
# n4: 0.000
# n5: 0.016
# n6: 0.000
# Averaged: 0.002
# -----------------------------------------------

# [20.00]: Simulation completed!
