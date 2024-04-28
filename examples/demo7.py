"""Example

Visualization tools."""
import os
import sys

PROJECT_NAME = 'RayCloudSim'
cur_path = os.path.abspath(os.path.dirname(__file__))
root_path = cur_path
while os.path.split(os.path.split(root_path)[0])[-1] != PROJECT_NAME:
    root_path = os.path.split(root_path)[0]
root_path = os.path.split(root_path)[0]
sys.path.append(root_path)

import pandas as pd

from core.env import Env
from core.task import Task

from examples.scenarios.scenario_3 import Scenario


def error_handler(error: Exception):
    pass

def main():
    # Create the Env
    scenario=Scenario(config_file="examples/scenarios/configs/config_3.json")
    env = Env(scenario, config_file="core/configs/env_config.json")

    # # Visualization: the topology
    # env.vis_graph(config_file="core/vis/configs/vis_config_base.json", 
    #               save_as="examples/vis/demo_3.png")

    # Load simulated tasks
    data = pd.read_csv("examples/dataset/demo3_dataset.csv")
    simulated_tasks = list(data.iloc[:].values)
    n_tasks = len(simulated_tasks)

    # Begin Simulation
    until = 1
    for task_info in simulated_tasks:
        # header = ['TaskName', 'GenerationTime', 'TaskID', 'TaskSize', 'CyclesPerBit', 
        #           'TransBitRate', 'DDL', 'SrcName', 'DstName']
        generated_time, dst_name = task_info[1], task_info[8]
        task = Task(task_id=task_info[2],
                    task_size=task_info[3],
                    cycles_per_bit=task_info[4],
                    trans_bit_rate=task_info[5],
                    ddl=task_info[6],
                    src_name=task_info[7],
                    task_name=task_info[0])

        while True:
            # Catch the returned info of completed tasks
            while env.done_task_info:
                item = env.done_task_info.pop(0)
                # print(f"[{item[0]}]: {item[1:]}")

            if env.now == generated_time:
                env.process(task=task, dst_name=dst_name)
                break

            # Execute the simulation with error handler
            try:
                env.run(until=until)
            except Exception as e:
                error_handler(e)

            until += 1

    # Continue the simulation until the last task successes/fails.
    while env.process_task_cnt < len(simulated_tasks):
        until += 1
        try:
            env.run(until=until)
        except Exception as e:
            error_handler(e)

    env.close()

    # Visualization: frames to video
    env.vis_frame2video()


if __name__ == '__main__':
    main()
