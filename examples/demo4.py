"""Example

Demo 4 is almost the same as Demo 3, except that it demonstrates how to
simulate multiple epochs.
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

import pandas as pd

from core.env import Env
from core.task import Task

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
    env = Env(scenario, config_file="core/configs/env_config.json")

    # # Visualize the topology
    # env.vis_graph(config_file="core/vis/configs/vis_config_base.json", 
    #               save_as="examples/vis/demo_3.png")

    # Load simulated tasks
    data = pd.read_csv("examples/dataset/demo3_dataset.csv")
    simulated_tasks = list(data.iloc[:].values)
    n_tasks = len(simulated_tasks)

    # Begin Simulation
    until = 1
    for _ in range(3):  # multiple epoch

        env.reset()
        base_until = until
        del dup_task_id_error[:]
        del net_no_path_error[:]
        del isolated_wireless_node_error[:]
        del net_cong_error[:]
        del insufficient_buffer_error[:]
        del timeout_error[:]

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

                if env.now - base_until == generated_time:
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
        for key, node in env.scenario.get_nodes().items():
            print(f"{key}: {node.energy_consumption:.3f}")
        print("-----------------------------------------------\n")

    env.close()


if __name__ == '__main__':
    main()


# # ==================== Simulation log ====================
# ...
# [3565.00]: Task {376} accomplished in Node {n8} with {110.00}s
# [3565.00]: **TimeoutError: Task {392}** timeout in Node {n8}
# [3565.00]: **TimeoutError: Task {397}** timeout in Node {n8}
# [3565.00]: **TimeoutError: Task {398}** timeout in Node {n8}
# [3574.00]: Task {396} accomplished in Node {n5} with {72.00}s

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

# n0: 4314949.120
# n1: 471212.800
# n2: 1595802.400
# n3: 382588.610
# n4: 3059439.000
# n5: 538638.350
# n6: 4145669.120
# n7: 1944716.800
# n8: 31345.600
# n9: 1301817.600
# -----------------------------------------------

# [3575.00]: Simulation completed!
