"""Example

Demo 4 is almost the same as Demo 3, except that it demonstrates how to
simulate multiple epochs.
"""
import os
import sys

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

from core.env import Env
from core.task import Task

# User should customize this class: Scenario
from examples.scenario.random_topology import Scenario

# Global statistics
dup_task_id_error = []
net_no_path_error = []
isolated_wireless_node_error = []
net_cong_error = []
no_cus_error = []
insufficient_buffer_error = []


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
    elif message[0] == 'NoFreeCUsError':
        # Error: no free CUs in the destination node
        # print(message[1])
        # ----- handle this error here -----
        no_cus_error.append(message[2])
    elif message[0] == 'InsufficientBufferError':
        # Error: insufficient buffer in the destination node
        # print(message[1])
        # ----- handle this error here -----
        insufficient_buffer_error.append(message[2])
    else:
        raise NotImplementedError(error)


def main():
    # Create the Env
    env = Env(scenario=Scenario())

    # # Visualize the scenario/network
    # env.vis_graph(save_as="vis/network_demo3.png")

    # Load simulated tasks
    with open("examples/demo3_dataset.txt", 'r') as f:
        simulated_tasks = eval(f.read())
        n_tasks = len(simulated_tasks)

    # Begin Simulation
    until = 1
    for _ in range(3):  # multiple epoch

        env.reset()
        base_until = until
        del dup_task_id_error[:]
        del net_no_path_error[:]
        del net_cong_error[:]
        del no_cus_error[:]

        for task_info in simulated_tasks:

            generated_time, task_attrs, dst_name = task_info
            task = Task(task_id=task_attrs[0],
                        max_cu=task_attrs[1],
                        task_size_exe=task_attrs[2],
                        task_size_trans=task_attrs[3],
                        bit_rate=task_attrs[4],
                        src_name=task_attrs[5],
                        task_name=task_attrs[6])

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
              f"NoFreeCUsError         : {len(no_cus_error)}\n"
              f"InsufficientBufferError: {len(insufficient_buffer_error)}")
        print("-----------------------------------------------\n")

    env.close()


if __name__ == '__main__':
    main()

# # ==================== Simulation log ====================
# ...
# [3266.09]: Processing Task {372} in {n8}
# [3267.00]: Task {372} accomplished in Node {n8} with {0.78}s
#
# -----------------------------------------------
# Done simulation with 400 tasks!
#
# DuplicateTaskIdError   : 0
# NetworkXNoPathError    : 0
# IsolatedWirelessNode   : 0
# NetCongestionError     : 11
# NoFreeCUsError         : 12
# InsufficientBufferError: 0
# -----------------------------------------------
#
# [3269.00]: Simulation completed!
