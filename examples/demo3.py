"""Example"""
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

# User should customize this class: Scenario
from examples.scenarios.random_topology import Scenario

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
    env = Env(scenario=Scenario())

    # # Visualize the scenario/network
    # env.vis_graph(save_as="examples/vis/network_demo3.png")

    # Load simulated tasks
    with open("examples/utils/demo3_dataset.txt", 'r') as f:
        simulated_tasks = eval(f.read())
        n_tasks = len(simulated_tasks)

    # Begin Simulation
    until = 1
    for task_info in simulated_tasks:

        generated_time, task_attrs, dst_name = task_info
        task = Task(task_id=task_attrs[0],
                    task_size=task_attrs[1],
                    cycles_per_bit=task_attrs[2],
                    trans_bit_rate=task_attrs[3],
                    ddl=task_attrs[4],
                    src_name=task_attrs[5],
                    task_name=task_attrs[6])

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
                env.run(until=until)  # execute the simulation step by step
            except Exception as e:
                error_handler(e)

            until += 1

    # Continue the simulation until the last task is completed.
    while env.process_task_cnt < len(simulated_tasks):
        until += 1
        try:
            env.run(until=until)  # execute the simulation step by step
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

    env.close()


if __name__ == '__main__':
    main()

# # ==================== Simulation log ====================
# ...
# [1085.00]: Task {365} accomplished in Node {n6} with {29.82}s
# [1085.00]: **TimeoutError: Task {384}** timeout in Node {n6}
# [1085.00]: Task {399} re-actives in Node {n6}
# [1085.00]: Processing Task {399} in {n6}
# [1087.00]: Task {399} accomplished in Node {n6} with {1.82}s

# -----------------------------------------------
# Done simulation with 400 tasks!

# DuplicateTaskIdError   : 0
# NetworkXNoPathError    : 0
# IsolatedWirelessNode   : 0
# NetCongestionError     : 0
# InsufficientBufferError: 65
# TimeoutError           : 1
# -----------------------------------------------

# [1088.00]: Simulation completed!
