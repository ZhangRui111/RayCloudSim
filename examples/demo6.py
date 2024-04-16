"""Evaluation

An example of evaluating the performance of offloading strategies using unified benchmarks.
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

from eval.benchmarks.caseA.small.scenario import Scenario  # testbed
from eval.metrics.metrics import SuccessRate, AvgLatency  # metric
from policies.demo.demo_random import DemoRandom  # policy


def main():
    # Init the Env
    env = Env(scenario=Scenario())

    # Init the policy
    policy = DemoRandom()

    # Begin Simulation
    until = 1
    for task_info in env.scenario.simulated_tasks:

        generated_time, task_attrs = task_info
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
                dst_id = policy.act(env, task)  # offloading decision
                dst_name = env.scenario.node_id2name[dst_id]
                env.process(task=task, dst_name=dst_name)
                break

            # Execute the simulation with error handler
            try:
                env.run(until=until)
            except Exception as e:
                pass

            until += 1

    # Continue the simulation until the last task successes/fails.
    while env.process_task_cnt < len(env.scenario.simulated_tasks):
        until += 1
        try:
            env.run(until=until)
        except Exception as e:
            pass

    # Evaluation
    print("\n-----------------------------------------------")
    print("Evaluation:\n")

    m1 = SuccessRate()
    r1 = m1.eval(env.logger.task_info)
    print(f"The success rate of all tasks: {r1:.3f}")

    m2 = AvgLatency()
    r2 = m2.eval(env.logger.task_info)
    print(f"The average latency per task: {r2:.3f}")

    print("-----------------------------------------------\n")

    env.close()


if __name__ == '__main__':
    main()
