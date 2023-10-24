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
    # env.vis_graph(save_as="vis/network_demo4.png")

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
