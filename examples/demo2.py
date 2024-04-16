"""Example

Example on how to obtain system status and catch various errors.
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

from core.env import Env
from core.task import Task

# User should customize this class: Scenario
from examples.scenarios.another_scenario import Scenario


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
    env = Env(scenario=Scenario())

    # # Visualize the scenario/network
    # env.vis_graph(save_as="examples/vis/network_demo2.png")
    
    # Note:
    #     (generated_time, 
    #      [task_id, task_size, cycles_per_bit, trans_bit_rate, 
    #       ddl, src_name, task_name], 
    #      dst_name)
    simulated_tasks = [
        # n0: local execution
        (0, [0, 20, 2, 10, 100, 'n0', 't0'], 'n0'),

        # n0 --> n2
        (0, [1, 20, 1, 10, 100, 'n0', 't1'], 'n2'),

        # Cause error: DuplicateTaskIdError
        (1, [0, 20, 1, 10, 100, 'n3', 't0-duplicate'], 'n3'),

        # Cause error: NetCongestionError
        (2, [2, 20, 1, 10, 100, 'n0', 't2'], 'n2'),

        # Cause error: NetworkXNoPathError
        (3, [3, 20, 1, 5, 100, 'n0', 't3'], 'n3'),

        # n0: local execution
        (4, [4, 20, 1, 10, 100, 'n0', 't4'], 'n0'),

        # Cause error: InsufficientBufferError
        (5, [5, 90, 1, 10, 100, 'n0', 't4'], 'n0'),

        # n0 --> n2
        (10, [6, 20, 1, 10, 100, 'n0', 't2-retry'], 'n2'),

        # n1: large task
        (20, [7, 20, 10, 10, 100, 'n1', 't5'], 'n1'),

        # Cause error: TimeoutError
        (20, [8, 20, 10, 10, 25, 'n1', 't6'], 'n1'),
    ]

    # Obtain system status
    n1_status = env.status(node_name='n1')
    link_n1_n2_status = env.status(link_args=('n1', 'n2'))
    init_status = env.status()

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

    # Continue the simulation until the last task successes/fails.
    while env.process_task_cnt < len(simulated_tasks):
        until += 1
        try:
            env.run(until=until)  # execute the simulation step by step
        except Exception as e:
            error_handler(e)

    print("\n-----------------------------------------------")
    print("Power consumption during simulation:\n")
    print(f"n0: {env.scenario.get_node('n0').power_consumption:.3f}")
    print(f"n1: {env.scenario.get_node('n1').power_consumption:.3f}")
    print(f"n2: {env.scenario.get_node('n2').power_consumption:.3f}")
    print(f"n3: {env.scenario.get_node('n3').power_consumption:.3f}")
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
# [8.00]: Task {4} re-actives in Node {n0}
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
# Power consumption during simulation:

# n0: 1375.610
# n1: 5000.610
# n2: 1000.610
# n3: 0.610
# -----------------------------------------------

# [60.00]: Simulation completed!
