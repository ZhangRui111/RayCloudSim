"""
This script demonstrates how to use the Pakistan dataset.
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
from core.vis.vis_stats import VisStats
from eval.benchmarks.Pakistan.scenario import Scenario
from eval.metrics.metrics import SuccessRate, AvgLatency  # metric
from policies.demo.demo_greedy import GreedyPolicy


def create_log_dir(algo_name, **params):
    """Creates a directory for storing the training/testing metrics logs.

    Args:
        algo_name (str): The name of the algorithm.
        **params: Additional parameters to be included in the directory name.

    Returns:
        str: The path to the created log directory.
    """
    # Create the algorithm-specific directory if it doesn't exist
    algo_dir = f"logs/{algo_name}"
    if not os.path.exists(algo_dir):
        os.makedirs(algo_dir)

    # Build the parameterized part of the directory name
    params_str = ""
    for key, value in params.items():
        params_str += f"{key}_{value}_"
    index = 0  # Find an available directory index
    log_dir = f"{algo_dir}/{params_str}{index}"
    while os.path.exists(log_dir):
        index += 1
        log_dir = f"{algo_dir}/{params_str}{index}"
    
    # Create the final log directory
    os.makedirs(log_dir, exist_ok=True)
    
    return log_dir


def main():
    flag = 'Tuple30K'
    # flag = 'Tuple50K'
    # flag = 'Tuple100K'
    
    # Create the environment with the specified scenario and configuration files.
    scenario=Scenario(config_file=f"eval/benchmarks/Pakistan/data/{flag}/config.json", flag=flag)
    env = Env(scenario, config_file="core/configs/env_config_null.json", verbose=True, decimal_places=3)

    # Load the test dataset.
    data = pd.read_csv(f"eval/benchmarks/Pakistan/data/{flag}/testset.csv")

    # Init the policy.
    policy = GreedyPolicy()

    # Begin the simulation.
    until = 0
    launched_task_cnt = 0
    path_dir = create_log_dir("vis/DemoGreedy", flag=flag)
    for i, task_info in data.iterrows():
        generated_time = task_info['GenerationTime']
        task = Task(task_id=task_info['TaskID'],
                    task_size=task_info['TaskSize'],
                    cycles_per_bit=task_info['CyclesPerBit'],
                    trans_bit_rate=task_info['TransBitRate'],
                    ddl=task_info['DDL'],
                    src_name='e0',
                    task_name=task_info['TaskName'])

        while True:
            # Catch completed task information.
            while env.done_task_info:
                item = env.done_task_info.pop(0)
            
            if env.now >= generated_time:
                dst_id = policy.act(env, task)  # offloading decision
                dst_name = env.scenario.node_id2name[dst_id]
                env.process(task=task, dst_name=dst_name)
                launched_task_cnt += 1
                break

            # Execute the simulation with error handler.
            try:
                env.run(until=until)
            except Exception as e:
                pass

            until += 1

    # Continue the simulation until the last task successes/fails.
    while env.task_count < launched_task_cnt:
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
    
    # Stats Visualization
    vis = VisStats(path_dir)
    vis.vis(env)


if __name__ == '__main__':
    main()
