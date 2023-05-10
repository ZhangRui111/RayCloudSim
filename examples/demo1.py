"""Hello World

A toy example.
"""
from core.env import Env
from core.task import Task

# User should customize this class: Scenario
from examples.scenario.simple_scenario import Scenario


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
