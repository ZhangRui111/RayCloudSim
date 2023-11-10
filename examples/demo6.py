"""Example

Example on buffer usage in computing nodes.
"""
import sys

from core.env import Env
from core.task import Task

# User should customize this class: Scenario
from examples.scenario.simple_scenario_3 import Scenario

sys.path.append('..')


def error_handler(error: Exception):
    """Customized error handler.

    In this example, we only care/handle two errors.
    """
    message = error.args[0]
    if message[0] == 'NoFreeCUsError':
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
        pass


def main():
    # Create the Env
    env = Env(scenario=Scenario())

    # # Visualize the scenario/network
    # env.vis_graph(save_as="vis/network_demo6.png")

    # dst_name = 'n0'
    # simulated_tasks = [
    #     (0, [0, 20, 50, 10, 20, 'n0', 't0'], dst_name),
    #     (1, [1, 20, 50, 10, 20, 'n0', 't1'], dst_name),
    #     (2, [2, 20, 50, 10, 20, 'n0', 't2'], dst_name),
    # ]

    simulated_tasks = [
        (0, [0, 20, 50, 10, 20, 'n0', 't0'], 'n0'),
        (1, [1, 20, 50, 10, 20, 'n0', 't1'], 'n0'),
        (2, [2, 20, 50, 10, 20, 'n0', 't2'], 'n1'),
        (3, [3, 20, 50, 10, 20, 'n1', 't3'], 'n1'),
        (4, [4, 20, 50, 10, 20, 'n1', 't4'], 'n2'),
        (5, [5, 20, 50, 10, 20, 'n2', 't5'], 'n2'),
        (6, [6, 20, 50, 10, 20, 'n2', 't6'], 'n0'),
        (7, [7, 20, 50, 10, 20, 'n2', 't7'], 'n1'),
    ]

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

    # Activate the last task.
    until += 1
    try:
        env.run(until=until)
    except Exception as e:
        error_handler(e)

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
# # 1. dst_name = 'n0'
# [0.00]: Task {0} generated in Node {n0}
# [0.00]: Processing Task {0} in {n0}
# [1.00]: Task {1} generated in Node {n0}
# [1.00]: Task {1} is buffered in Node {n0}
# [2.00]: Task {2} generated in Node {n0}
# [2.00]: **InsufficientBufferError: Task {2}** insufficient buffer in Node {n0}
# [3.00]: Task {0} accomplished in Node {n0} with {2.50}s
# [3.00]: Task {1} re-actives in Node {n0}
# [3.00]: Processing Task {1} in {n0}
# [6.00]: Task {1} accomplished in Node {n0} with {2.50}s
# [7.00]: Simulation completed!
#
# # 2. dst_name = 'n1'
# [0.00]: Task {0} generated in Node {n0}
# [0.00]: Task {0}: {n0} --> {n1}
# [1.00]: Task {1} generated in Node {n0}
# [1.00]: Task {1}: {n0} --> {n1}
# [2.00]: Task {2} generated in Node {n0}
# [2.00]: Task {2}: {n0} --> {n1}
# [4.00]: Task {0} arrived Node {n1} with {4.00}s
# [4.00]: Processing Task {0} in {n1}
# [5.00]: Task {1} arrived Node {n1} with {4.00}s
# [5.00]: **NoFreeCUsError: Task {1}** no free CUs in Node {n1}
# [6.00]: Task {2} arrived Node {n1} with {4.00}s
# [6.00]: **NoFreeCUsError: Task {2}** no free CUs in Node {n1}
# [7.00]: Task {0} accomplished in Node {n1} with {2.50}s
# [8.00]: Simulation completed!
#
# # 3. dst_name = 'n2'
# [0.00]: Task {0} generated in Node {n0}
# [0.00]: Task {0}: {n0} --> {n2}
# [1.00]: Task {1} generated in Node {n0}
# [1.00]: Task {1}: {n0} --> {n2}
# [2.00]: Task {2} generated in Node {n0}
# [2.00]: Task {2}: {n0} --> {n2}
# [8.00]: Task {0} arrived Node {n2} with {8.00}s
# [8.00]: Processing Task {0} in {n2}
# [9.00]: Task {1} arrived Node {n2} with {8.00}s
# [9.00]: Task {1} is buffered in Node {n2}
# [10.00]: Task {2} arrived Node {n2} with {8.00}s
# [10.00]: Task {2} is buffered in Node {n2}
# [11.00]: Task {0} accomplished in Node {n2} with {2.50}s
# [11.00]: Task {1} re-actives in Node {n2}
# [11.00]: Processing Task {1} in {n2}
# [14.00]: Task {1} accomplished in Node {n2} with {2.50}s
# [14.00]: Task {2} re-actives in Node {n2}
# [14.00]: Processing Task {2} in {n2}
# [17.00]: Task {2} accomplished in Node {n2} with {2.50}s
# [18.00]: Simulation completed!
#
# # 4. simulated_tasks with 8 tasks:
# [0.00]: Task {0} generated in Node {n0}
# [0.00]: Processing Task {0} in {n0}
# [1.00]: Task {1} generated in Node {n0}
# [1.00]: Task {1} is buffered in Node {n0}
# [2.00]: Task {2} generated in Node {n0}
# [2.00]: Task {2}: {n0} --> {n1}
# [3.00]: Task {3} generated in Node {n1}
# [3.00]: Processing Task {3} in {n1}
# [3.00]: Task {0} accomplished in Node {n0} with {2.50}s
# [3.00]: Task {1} re-actives in Node {n0}
# [3.00]: Processing Task {1} in {n0}
# [4.00]: Task {4} generated in Node {n1}
# [4.00]: Task {4}: {n1} --> {n2}
# [5.00]: Task {5} generated in Node {n2}
# [5.00]: Processing Task {5} in {n2}
# [6.00]: Task {6} generated in Node {n2}
# [6.00]: Task {6}: {n2} --> {n0}
# [6.00]: Task {2} arrived Node {n1} with {4.00}s
# [6.00]: **NoFreeCUsError: Task {2}** no free CUs in Node {n1}
# [6.00]: Task {3} accomplished in Node {n1} with {2.50}s
# [6.00]: Task {1} accomplished in Node {n0} with {2.50}s
# [7.00]: Task {7} generated in Node {n2}
# [7.00]: Task {7}: {n2} --> {n1}
# [8.00]: Task {4} arrived Node {n2} with {4.00}s
# [8.00]: Task {4} is buffered in Node {n2}
# [8.00]: Task {5} accomplished in Node {n2} with {2.50}s
# [8.00]: Task {4} re-actives in Node {n2}
# [8.00]: Processing Task {4} in {n2}
# [11.00]: Task {7} arrived Node {n1} with {4.00}s
# [11.00]: Processing Task {7} in {n1}
# [11.00]: Task {4} accomplished in Node {n2} with {2.50}s
# [14.00]: Task {6} arrived Node {n0} with {8.00}s
# [14.00]: Processing Task {6} in {n0}
# [14.00]: Task {7} accomplished in Node {n1} with {2.50}s
# [17.00]: Task {6} accomplished in Node {n0} with {2.50}s
# [18.00]: Simulation completed!
