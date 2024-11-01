"""Example

Example on how to obtain system status and catch various errors.
"""
import os
import sys

current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from core.env import Env
from core.task import Task
from core.vis import *

from examples.scenarios.scenario_2 import Scenario


def error_handler(error: Exception):
    """Customized error handler."""
    message = error.args[0]
    if message[0] == 'DuplicateTaskIdError':
        # Error: duplicate task id
        # print(message[1])
        # ----- handle this error here -----
        pass
    elif message[0] == 'NetworkXNoPathError':
        # Error: nx.exception.NetworkXNoPath
        # print(message[1])
        # ----- handle this error here -----
        pass
    elif message[0] == 'IsolatedWirelessNode':
        # Error: isolated wireless src/dst node
        # print(message[1])
        # ----- handle this error here -----
        pass
    elif message[0] == 'NetCongestionError':
        # Error: network congestion
        # print(message[1])
        # ----- handle this error here -----
        pass
    elif message[0] == 'InsufficientBufferError':
        # Error: insufficient buffer in the destination node
        # print(message[1])
        # ----- handle this error here -----
        pass
    elif message[0] == 'TimeoutError':
        # Error: the task is not executed before the deadline (ddl).
        # print(message[1])
        # ----- handle this error here -----
        pass
    else:
        raise NotImplementedError(error)


def main():
    # Create the Env
    scenario=Scenario(config_file="examples/scenarios/configs/config_2.json")
    env = Env(scenario, config_file="core/configs/env_config_null.json")

    # # Visualization: the topology
    # vis_graph(env,
    #           config_file="core/vis/configs/vis_config_base.json", 
    #           save_as="examples/vis/demo_2.png")
    
    # header = ['TaskName', 'GenerationTime', 'TaskID', 'TaskSize', 'CyclesPerBit', 
    #           'TransBitRate', 'DDL', 'SrcName', 'DstName']
    simulated_tasks = [
        # n0: local execution
        ('t0', 0, 0, 20, 2, 10, 100, 'n0', 'n0'),

        # n0 --> n2
        ('t1', 0, 1, 20, 1, 10, 100, 'n0', 'n2'),

        # Cause error: DuplicateTaskIdError
        ('t0-duplicate', 1, 0, 20, 1, 10, 100, 'n3', 'n3'),

        # Cause error: NetCongestionError
        ('t2', 2, 2, 20, 1, 10, 100, 'n0', 'n2'),

        # Cause error: NetworkXNoPathError
        ('t3', 3, 3, 20, 1, 5, 100, 'n0', 'n3'),

        # n0: local execution
        ('t4', 4, 4, 20, 1, 10, 100, 'n0', 'n0'),

        # Cause error: InsufficientBufferError
        ('t4', 5, 5, 90, 1, 10, 100, 'n0', 'n0'),

        # n0 --> n2
        ('t2-retry', 10, 6, 20, 1, 10, 100, 'n0', 'n2'),

        # n1: large task
        ('t5', 20, 7, 20, 10, 10, 100, 'n1', 'n1'),

        # Cause error: TimeoutError
        ('t6', 20, 8, 20, 10, 10, 25, 'n1', 'n1'),
    ]

    # Obtain system status
    n1_status = env.status(node_name='n1')
    link_n1_n2_status = env.status(link_args=('n1', 'n2'))
    init_status = env.status()

    # Begin Simulation
    until = 1
    for task_info in simulated_tasks:

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
                env.run(until=until)  # execute the simulation step by step
            except Exception as e:
                error_handler(e)

            until += 1

    # Continue the simulation until the last task successes/fails.
    while env.process_task_cnt < len(simulated_tasks):
        until += 1
        try:
            env.run(until=until)  # execute the simulation step by step
        except Exception as e:
            error_handler(e)

    print("\n-----------------------------------------------")
    print("Energy consumption during simulation:\n")
    print(f"n0: {env.node_energy('n0'):.3f}")
    print(f"n1: {env.node_energy('n1'):.3f}")
    print(f"n2: {env.node_energy('n2'):.3f}")
    print(f"n3: {env.node_energy('n3'):.3f}")
    print(f"Averaged: {env.avg_node_energy():.3f}")
    print(f"Averaged ('n0', 'n1'): {env.avg_node_energy(node_name_list=['n0', 'n1']):.3f}")
    print("-----------------------------------------------\n")

    env.close()


if __name__ == '__main__':
    main()


# # ==================== Simulation log ====================
# [0.00]: Task {0} generated in Node {n0}
# [0.00]: Processing Task {0} in {n0}
# [0.00]: Task {1} generated in Node {n0}
# [0.00]: Task {1}: {n0} --> {n2}
# [1.00]: **DuplicateTaskIdError: Task {0}** new task (name {t0-duplicate}) with a duplicate task id {0}.
# [2.00]: Task {2} generated in Node {n0}
# [2.00]: **NetCongestionError: Task {2}** network congestion Node {n0} --> {n2}
# [3.00]: Task {3} generated in Node {n0}
# [3.00]: **NetworkXNoPathError: Task {3}** Node {n3} is inaccessible
# [4.00]: Task {4} generated in Node {n0}
# [4.00]: Task {4} is buffered in Node {n0}
# [4.00]: Task {1} arrived Node {n2} with {4.00}s
# [4.00]: Processing Task {1} in {n2}
# [5.00]: Task {5} generated in Node {n0}
# [5.00]: **InsufficientBufferError: Task {5}** insufficient buffer in Node {n0}
# [8.00]: Task {0} accomplished in Node {n0} with {8.00}s
# [8.00]: Task {1} accomplished in Node {n2} with {4.00}s
# [8.00]: Task {4} re-actives in Node {n0}, waiting {4.00}s
# [8.00]: Processing Task {4} in {n0}
# [10.00]: Task {6} generated in Node {n0}
# [10.00]: Task {6}: {n0} --> {n2}
# [12.00]: Task {4} accomplished in Node {n0} with {4.00}s
# [14.00]: Task {6} arrived Node {n2} with {4.00}s
# [14.00]: Processing Task {6} in {n2}
# [18.00]: Task {6} accomplished in Node {n2} with {4.00}s
# [20.00]: Task {7} generated in Node {n1}
# [20.00]: Processing Task {7} in {n1}
# [20.00]: Task {8} generated in Node {n1}
# [20.00]: Task {8} is buffered in Node {n1}
# [60.00]: Task {7} accomplished in Node {n1} with {40.00}s
# [60.00]: **TimeoutError: Task {8}** timeout in Node {n1}

# -----------------------------------------------
# Energy consumption during simulation:

# n0: 0.001
# n1: 0.005
# n2: 0.001
# n3: 0.000
# Averaged: 0.002
# Averaged ('n0', 'n1'): 0.003
# -----------------------------------------------

# [60.00]: Simulation completed!
