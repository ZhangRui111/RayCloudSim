"""Example

Example on simulation that considers the wireless transmission.
"""
import sys

from core.env import Env
from core.task import Task

# User should customize this class: Scenario
from examples.scenario.simple_scenario_2 import Scenario

sys.path.append('..')


def main():
    # Create the Env
    env = Env(scenario=Scenario())

    # # Visualize the scenario/network
    # env.vis_graph(save_as="vis/network_demo5.png")

    # Begin Simulation
    task1 = Task(task_id=0,
                 max_cu=10,
                 task_size_exe=20,
                 task_size_trans=10,
                 bit_rate=20,
                 src_name='n4')

    env.process(task=task1, dst_name='n5')

    env.run(until=10)  # execute the simulation until 10

    task2 = Task(task_id=1,
                 max_cu=10,
                 task_size_exe=20,
                 task_size_trans=10,
                 bit_rate=20,
                 src_name='n1')

    env.process(task=task2, dst_name='n5')

    env.run(until=20)  # execute the simulation from 10 to 20

    env.close()


if __name__ == '__main__':
    main()

# # ==================== Simulation log ====================
# [0.00]: Task {0} generated in Node {n4}
# [0.00]: Task {0}: {n4} --> {n5}
# [10.00]: Task {1} generated in Node {n1}
# [10.00]: Task {1}: {n1} --> {n5}
# [12.00]: Task {0} arrived Node {n5} with {12.00}s
# [12.00]: Processing Task {0} in {n5}
# [14.00]: Task {0} accomplished in Node {n5} with {2.00}s
# [18.00]: Task {1} arrived Node {n5} with {8.00}s
# [18.00]: Processing Task {1} in {n5}
# [20.00]: Simulation completed!
