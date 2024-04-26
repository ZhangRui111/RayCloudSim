"""Hello World

A toy example.
"""
import os
import sys

PROJECT_NAME = 'RayCloudSim'
cur_path = os.path.abspath(os.path.dirname(__file__))
root_path = cur_path
while os.path.split(os.path.split(root_path)[0])[-1] != PROJECT_NAME:
    root_path = os.path.split(root_path)[0]
root_path = os.path.split(root_path)[0]
sys.path.append(root_path)

from core.env import Env
from core.task import Task

from examples.scenarios.scenario_1 import Scenario


def main():
    # Create the Env
    env = Env(
        scenario=Scenario(
            config_file="examples/scenarios/configs/config_1.json"))

    # # Visualize the scenario/network
    # env.vis_graph(save_as="examples/vis/network_demo1.png")

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
    print(f"n0: {env.scenario.get_node('n0').energy_consumption:.3f}")
    print(f"n1: {env.scenario.get_node('n1').energy_consumption:.3f}")
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
# -----------------------------------------------

# [20.00]: Simulation completed!
