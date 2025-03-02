"""
This script demonstrates error handling for common network and task issues.
"""

import os
import sys

current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

import pandas as pd

from core.env import Env
from core.task import Task
from core.vis import *
from examples.scenarios.scenario_3 import Scenario

# Global statistics for different error types
dup_task_id_error = []
net_no_path_error = []
isolated_wireless_node_error = []
net_cong_error = []
insufficient_buffer_error = []


def error_handler(error: Exception):
    """Customized error handler for different types of errors."""

    message = error.args[0]

    if message[0] == 'DuplicateTaskIdError':
        # Error: duplicate task id
        # print(message[1])
        # ----- handle this error here -----
        dup_task_id_error.append(message[2])
    elif message[0] == 'NetworkXNoPathError':
        # Error: nx.exception.NetworkXNoPath
        # print(message[1])
        # ----- handle this error here -----
        net_no_path_error.append(message[2])
    elif message[0] == 'IsolatedWirelessNode':
        # Error: isolated wireless src/dst node
        # print(message[1])
        # ----- handle this error here -----
        isolated_wireless_node_error.append(message[2])
    elif message[0] == 'NetCongestionError':
        # Error: network congestion
        # print(message[1])
        # ----- handle this error here -----
        net_cong_error.append(message[2])
    elif message[0] == 'InsufficientBufferError':
        # Error: insufficient buffer in the destination node
        # print(message[1])
        # ----- handle this error here -----
        insufficient_buffer_error.append(message[2])
    else:
        raise NotImplementedError(error)


def main():
    # Create the environment with the specified scenario and configuration files.
    scenario = Scenario(config_file="examples/scenarios/configs/config_3.json")
    env = Env(scenario, config_file="core/configs/env_config_null.json")

    # Visualization: Display the topology of the environment.
    # vis_graph(env,
    #           config_file="core/vis/configs/vis_config_base.json", 
    #           save_as="examples/vis/demo_3.png")

    # Load simulated tasks from the CSV dataset.
    data = pd.read_csv("examples/dataset/demo3_dataset.csv")
    simulated_tasks = list(data.iloc[:].values)
    n_tasks = len(simulated_tasks)

    # Begin the simulation.
    until = 1
    launched_task_cnt = 0
    timeout_task_cnt = 0
    for task_info in simulated_tasks:
        # Task properties:
        # ['TaskName', 'GenerationTime', 'TaskID', 'TaskSize', 'CyclesPerBit', 
        #  'TransBitRate', 'DDL', 'SrcName', 'DstName']
        generated_time, dst_name = task_info[1], task_info[8]
        task = Task(task_id=task_info[2],
                    task_size=task_info[3],
                    cycles_per_bit=task_info[4],
                    trans_bit_rate=task_info[5],
                    ddl=task_info[6],
                    src_name=task_info[7],
                    task_name=task_info[0])

        while True:
            # Catch completed task information.
            while env.done_task_info:
                item = env.done_task_info.pop(0)
                info = item[3]
                if not info[1]['ddl_ok']:
                    timeout_task_cnt += 1

            if abs(env.now - generated_time) < 1e-6:
                env.process(task=task, dst_name=dst_name)
                launched_task_cnt += 1
                break

            # Execute the simulation with error handler.
            try:
                env.run(until=until)
            except Exception as e:
                error_handler(e)

            until += 1

    # Continue the simulation until the last task successes/fails.
    while env.task_count < launched_task_cnt:
        until += 1
        try:
            env.run(until=until)
        except Exception as e:
            error_handler(e)

    print("\n-----------------------------------------------")
    print(f"Done simulation with {n_tasks} tasks!\n\n"
          f"DuplicateTaskIdError   : {len(dup_task_id_error)}\n"
          f"NetworkXNoPathError    : {len(net_no_path_error)}\n"
          f"IsolatedWirelessNode   : {len(isolated_wireless_node_error)}\n"
          f"NetCongestionError     : {len(net_cong_error)}\n"
          f"InsufficientBufferError: {len(insufficient_buffer_error)}")
    print("-----------------------------------------------\n")

    print(f"There are {timeout_task_cnt} time-out tasks.")

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
# ...
# [1178.0]: Processing Task {369} in {n8}
# [1208.0]: Task {369}: Accomplished in Node {n8} with execution time {30.0}s
# [1208.0]: Task {376} re-actives in Node {n8}, waiting {269.7}s
# [1208.0]: Processing Task {376} in {n8}
# [1318.0]: Task {376}: Accomplished in Node {n8} with execution time {109.8}s

# -----------------------------------------------
# Done simulation with 400 tasks!

# DuplicateTaskIdError   : 0
# NetworkXNoPathError    : 0
# IsolatedWirelessNode   : 0
# NetCongestionError     : 6
# InsufficientBufferError: 70
# -----------------------------------------------

# There are 56 time-out tasks.

# -----------------------------------------------
# Energy consumption during simulation:

# n0: 4.155
# n1: 0.474
# n2: 1.755
# n3: 0.380
# n4: 2.965
# n5: 0.535
# n6: 4.037
# n7: 1.992
# n8: 0.039
# n9: 1.355
# Averaged: 1.769
# -----------------------------------------------

# [1319.0]: Simulation completed!
