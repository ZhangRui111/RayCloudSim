"""Example"""
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

# Global statistics
dup_task_id_error = []
net_no_path_error = []
isolated_wireless_node_error = []
net_cong_error = []
insufficient_buffer_error = []
timeout_error = []


def error_handler(error: Exception):
    """Customized error handler."""
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
    elif message[0] == 'TimeoutError':
        # Error: the task is not executed before the deadline (ddl).
        # print(message[1])
        # ----- handle this error here -----
        timeout_error.append(message[2])
    else:
        raise NotImplementedError(error)


def main():
    # Create the Env
    scenario=Scenario(config_file="examples/scenarios/configs/config_3.json")
    env = Env(scenario, config_file="core/configs/env_config_null.json")

    # # Visualization: the topology
    # vis_graph(env,
    #           config_file="core/vis/configs/vis_config_base.json", 
    #           save_as="examples/vis/demo_3.png")

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

            if abs(env.now - generated_time) < 1e-6:
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

    print("\n-----------------------------------------------")
    print(f"Done simulation with {n_tasks} tasks!\n\n"
          f"DuplicateTaskIdError   : {len(dup_task_id_error)}\n"
          f"NetworkXNoPathError    : {len(net_no_path_error)}\n"
          f"IsolatedWirelessNode   : {len(isolated_wireless_node_error)}\n"
          f"NetCongestionError     : {len(net_cong_error)}\n"
          f"InsufficientBufferError: {len(insufficient_buffer_error)}\n"
          f"TimeoutError           : {len(timeout_error)}")
    print("-----------------------------------------------\n")

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
# [1093.00]: Task {376} accomplished in Node {n8} with {110.00}s
# [1093.00]: **TimeoutError: Task {392}** timeout in Node {n8}
# [1093.00]: **TimeoutError: Task {397}** timeout in Node {n8}
# [1093.00]: **TimeoutError: Task {398}** timeout in Node {n8}
# [1102.00]: Task {396} accomplished in Node {n5} with {72.00}s

# -----------------------------------------------
# Done simulation with 400 tasks!

# DuplicateTaskIdError   : 0
# NetworkXNoPathError    : 0
# IsolatedWirelessNode   : 0
# NetCongestionError     : 6
# InsufficientBufferError: 56
# TimeoutError           : 26
# -----------------------------------------------


# -----------------------------------------------
# Energy consumption during simulation:

# n0: 4.315
# n1: 0.471
# n2: 1.596
# n3: 0.383
# n4: 3.059
# n5: 0.539
# n6: 4.146
# n7: 1.945
# n8: 0.031
# n9: 1.302
# Averaged: 1.779
# -----------------------------------------------

# [1103.00]: Simulation completed!
