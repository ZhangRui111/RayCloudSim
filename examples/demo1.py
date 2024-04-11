"""Hello World

A toy example.
"""
import os
import sys

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

from core.env import Env
from core.task import Task

# User should customize this class: Scenario
from examples.scenario.simple_scenario_1 import Scenario


def main():
    # Create the Env
    env = Env(scenario=Scenario())

    # # Visualize the scenario/network
    # env.vis_graph(save_as="vis/network_demo1.png")

    # Begin Simulation
    task = Task(task_id=0,
                max_cu=10,
                task_size_exe=20,
                task_size_trans=10,
                bit_rate=20,
                src_name='n0')

    env.process(task=task, dst_name='n1')

    env.run(until=10)  # execute the simulation all at once

    env.close()


if __name__ == '__main__':
    main()

# # ==================== Simulation log ====================
# [0.00]: Task {0} generated in Node {n0}
# [0.00]: Task {0}: {n0} --> {n1}
# [4.00]: Task {0} arrived Node {n1} with {4.00}s
# [4.00]: Processing Task {0} in {n1}
# [6.00]: Task {0} accomplished in Node {n1} with {2.00}s
# [10.00]: Simulation completed!
