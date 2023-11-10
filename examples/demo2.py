"""Example

Example on how to obtain system status and catch various errors.
"""
import sys

from core.env import Env
from core.task import Task

# User should customize this class: Scenario
from examples.scenario.another_scenario import Scenario

sys.path.append('..')


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
    elif message[0] == 'NoFreeCUsError':
        # Error: no free CUs in the destination node
        # print(message[1])
        # ----- handle this error here -----
        pass
    elif message[0] == 'InsufficientBufferError':
        # Error: insufficient buffer in the destination node
        # print(message[1])
        # ----- handle this error here -----
        pass
    else:
        raise NotImplementedError(error)


def main():
    # Create the Env
    env = Env(scenario=Scenario())

    # # Visualize the scenario/network
    # env.vis_graph(save_as="vis/network_demo2.png")

    simulated_tasks = [
        # n0: local execution
        (0, [0, 10, 20, 10, 20, 'n0', 't0'], 'n0'),

        # n0 --> n2
        (0, [1, 10, 20, 10, 20, 'n0', 't1'], 'n2'),

        # Cause error: DuplicateTaskIdError
        (1, [0, 1, 2, 1, 2, 'n3', 't0-duplicate'], 'n3'),

        # Cause error: NetCongestionError
        (2, [2, 10, 20, 10, 20, 'n0', 't2'], 'n2'),

        # Cause error: NetworkXNoPathError
        (3, [3, 10, 20, 10, 20, 'n0', 't3'], 'n3'),

        # n0: local execution
        (4, [4, 20, 20, 10, 20, 'n0', 't4'], 'n0'),

        # Cause error: NoFreeCUsError
        (4, [5, 10, 20, 10, 20, 'n0', 't5'], 'n0'),

        # n0 --> n2
        (10, [6, 10, 20, 10, 20, 'n0', 't2-again'], 'n2'),
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
            env.run(until=until)
        except Exception as e:
            error_handler(e)

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
# [2.00]: Task {0} accomplished in Node {n0} with {2.00}s
# [3.00]: Task {3} generated in Node {n0}
# [3.00]: **NetworkXNoPathError: Task {3}** Node {n3} is inaccessible
# [4.00]: Task {4} generated in Node {n0}
# [4.00]: Processing Task {4} in {n0}
# [4.00]: Task {5} generated in Node {n0}
# [4.00]: **NoFreeCUsError: Task {5}** no free CUs in Node {n0}
# [5.00]: Task {4} accomplished in Node {n0} with {1.00}s
# [8.00]: Task {1} arrived Node {n2} with {8.00}s
# [8.00]: Processing Task {1} in {n2}
# [10.00]: Task {6} generated in Node {n0}
# [10.00]: Task {6}: {n0} --> {n2}
# [10.00]: Task {1} accomplished in Node {n2} with {2.00}s
# [18.00]: Task {6} arrived Node {n2} with {8.00}s
# [18.00]: Processing Task {6} in {n2}
# [20.00]: Task {6} accomplished in Node {n2} with {2.00}s
# [21.00]: Simulation completed!
