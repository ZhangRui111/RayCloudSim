"""Example

Demo 4 is almost the same as Demo 3, except that it demonstrates how to
simulate multiple epochs.
"""
import sys

from core.env import Env
from core.task import Task

# User should customize this class: Scenario
from examples.scenario.random_topology import Scenario

sys.path.append('..')


def main():
    # Create the Env
    env = Env(scenario=Scenario())

    # # Visualize the scenario/network
    # env.vis_graph(save_as="vis/network_demo3.png")

    # Load simulated tasks
    with open("demo3_dataset.txt", 'r') as f:
        simulated_tasks = eval(f.read())
        n_tasks = len(simulated_tasks)

    # Begin Simulation
    until = 1
    for _ in range(3):  # multiple epoch

        env.reset()
        base_until = until
        dup_task_id_error, net_no_path_error, net_cong_error, no_cus_error = \
            [], [], [], []  # statistics

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

                try:
                    env.run(until=until)  # execute the simulation step by step
                except Exception as e:
                    message = e.args[0]
                    if message[0] == 'DuplicateTaskIdError':
                        # Error: duplicate task id
                        env.logger.log(message[1])
                        # ----- handle this error here -----
                        dup_task_id_error.append(message[2])
                        pass
                    elif message[0] == 'NetworkXNoPathError':
                        # Error: nx.exception.NetworkXNoPath
                        env.logger.log(message[1])
                        # ----- handle this error here -----
                        net_no_path_error.append(message[2])
                        pass
                    elif message[0] == 'NetCongestionError':
                        # Error: network congestion
                        env.logger.log(message[1])
                        # ----- handle this error here -----
                        net_cong_error.append(message[2])
                        pass  # TODO: tolerate time
                    elif message[0] == 'NoFreeCUsError':
                        # Error: no free CUs in the destination node
                        env.logger.log(message[1])
                        # ----- handle this error here -----
                        no_cus_error.append(message[2])
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

        print("\n-----------------------------------------------")
        print(f"Done simulation with {n_tasks} tasks!\n\n"
              f"DuplicateTaskIdError: {len(dup_task_id_error)}\n"
              f"NetworkXNoPathError : {len(net_no_path_error)}\n"
              f"NetCongestionError  : {len(net_cong_error)}\n"
              f"NoFreeCUsError      : {len(no_cus_error)}")
        print("-----------------------------------------------\n")

    env.close()


if __name__ == '__main__':
    main()
