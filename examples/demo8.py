"""Example on how to use the Topo4MEC dataset.
"""
import os
import sys

current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

import pandas as pd

from core.env import Env
from core.task import Task
from core.vis import *

from eval.benchmarks.Topo4MEC.scenario import Scenario
from eval.metrics.metrics import SuccessRate, AvgLatency  # metric
from policies.demo.demo_random import DemoRandom  # policy


def main():
    flag = '25N50E'
    # flag = '50N50E'
    # flag = '100N150E'
    # flag = 'MilanCityCenter'

    # Create the Env
    scenario=Scenario(config_file=f"eval/benchmarks/Topo4MEC/data/{flag}/config.json", flag=flag)
    env = Env(scenario, config_file="core/configs/env_config_null.json")

    # Load the test dataset
    data = pd.read_csv(f"eval/benchmarks/Topo4MEC/data/{flag}/testset.csv")
    test_tasks = list(data.iloc[:].values)

    # Init the policy
    policy = DemoRandom()

    # Begin Simulation
    until = 1
    for task_info in test_tasks:
        # header = ['TaskName', 'GenerationTime', 'TaskID', 'TaskSize', 'CyclesPerBit', 
        #           'TransBitRate', 'DDL', 'SrcName']  # field names
        generated_time = task_info[1]
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
    while env.process_task_cnt < len(test_tasks):
        until += 1
        try:
            env.run(until=until)
        except Exception as e:
            pass

    # Evaluation
    print("\n===============================================")
    print("Evaluation:")
    print("===============================================\n")

    print("-----------------------------------------------")
    m1 = SuccessRate()
    r1 = m1.eval(env.logger.task_info)
    print(f"The success rate of all tasks: {r1:.4f}")
    print("-----------------------------------------------\n")

    print("-----------------------------------------------")
    m2 = AvgLatency()
    r2 = m2.eval(env.logger.task_info)
    print(f"The average latency per task: {r2:.4f}")

    print(f"The average energy consumption per node: {env.avg_node_energy():.4f}")
    print("-----------------------------------------------\n")

    env.close()


if __name__ == '__main__':
    main()
