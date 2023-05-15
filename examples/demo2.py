"""Example

Example on how to obtain system status and catch various errors.
"""
import sys

from core.env import Env
from core.task import Task

# User should customize this class: Scenario
from examples.scenario.another_scenario import Scenario

sys.path.append('..')


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

            try:
                env.run(until=until)  # execute the simulation step by step
            except Exception as e:
                message = e.args[0]
                if message[0] == 'DuplicateTaskIdError':
                    # Error: duplicate task id
                    env.logger.log(message[1])
                    # ----- handle this error here -----
                    pass
                elif message[0] == 'NetworkXNoPathError':
                    # Error: nx.exception.NetworkXNoPath
                    env.logger.log(message[1])
                    # ----- handle this error here -----
                    pass
                elif message[0] == 'NetCongestionError':
                    # Error: network congestion
                    env.logger.log(message[1])
                    # ----- handle this error here -----
                    pass  # TODO: tolerate time
                elif message[0] == 'NoFreeCUsError':
                    # Error: no free CUs in the destination node
                    env.logger.log(message[1])
                    # ----- handle this error here -----
                    pass  # TODO: tolerate time
                else:
                    raise NotImplementedError(e)

            until += 1

    # Activate the last task.
    until += 1
    env.run(until=until)
    # Continue the simulation until the last task is completed.
    while env.n_active_tasks > 0:
        until += 1
        env.run(until=until)

    env.close()


if __name__ == '__main__':
    main()
