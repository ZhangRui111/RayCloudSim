"""Example

Example on simulation that considers the wireless transmission.
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

from examples.scenarios.scenario_5 import Scenario


def main():
    # Create the Env
    scenario=Scenario(config_file="examples/scenarios/configs/config_5.json")
    env = Env(scenario, config_file="core/configs/env_config.json")

    # # Visualize the topology
    # env.vis_graph(config_file="core/vis/configs/vis_config_base.json", 
    #               save_as="examples/vis/demo_5.png")

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
    print(f"n0: {env.scenario.get_node('n0').energy_consumption:.3f}")
    print(f"n1: {env.scenario.get_node('n1').energy_consumption:.3f}")
    print(f"n2: {env.scenario.get_node('n2').energy_consumption:.3f}")
    print(f"n3: {env.scenario.get_node('n3').energy_consumption:.3f}")
    print(f"n4: {env.scenario.get_node('n4').energy_consumption:.3f}")
    print(f"n5: {env.scenario.get_node('n5').energy_consumption:.3f}")
    print(f"n6: {env.scenario.get_node('n6').energy_consumption:.3f}")
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

# n0: 0.200
# n1: 0.200
# n2: 0.200
# n3: 0.200
# n4: 0.200
# n5: 1600.200
# n6: 0.200
# -----------------------------------------------

# [20.00]: Simulation completed!
