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
from core.vis.logger import Logger
from eval.benchmarks.Pakistan.scenario import Scenario
from eval.metrics.metrics import SuccessRate, AvgLatency  # metric
from policies.demo.demo_greedy import GreedyPolicy
from policies.demo.demo_random import DemoRandom
from policies.demo.demo_round_robin import RoundRobinPolicy

def create_env(config):
    """
    Creates the environment using configuration parameters.
    """
    flag = config["env"]["flag"]
    # Create scenario using the provided config file.
    scenario = Scenario(config_file=f"eval/benchmarks/Pakistan/data/{flag}/config.json", flag=flag)
    env = Env(scenario, config_file="core/configs/env_config_null.json", verbose=False, decimal_places=3)
    env.refresh_rate = config["env"]["refresh_rate"]
    return env

def main():
    # Define configuration dictionary (acting as a config file).
    config = {
        "env": {
            "dataset": "Pakistan",
            "flag": "Tuple30K",  # Can change to Tuple50K or Tuple100K if desired.
            "refresh_rate": 0.001
        },
        "policy": "DemoGreedy",
    }
    
    # Initialize the logger.
    logger = Logger(config)
    
    # Create the environment.
    env = create_env(config)
    
    # Load the test dataset.
    flag = config["env"]["flag"]
    data = pd.read_csv(f"eval/benchmarks/Pakistan/data/{flag}/testset.csv")

    # Init the policy.
    if config["policy"] == "DemoGreedy":
        policy = GreedyPolicy()
    elif config["policy"] == "DemoRandom":
        policy = DemoRandom()
    elif config["policy"] == "DemoRoundRobin":
        policy = RoundRobinPolicy()
    else:
        raise ValueError("Invalid policy name.")

    # Begin the simulation.
    until = 0
    launched_task_cnt = 0
    for i, task_info in data.iterrows():
        generated_time = task_info['GenerationTime']
        task = Task(task_id=task_info['TaskID'],
                    task_size=task_info['TaskSize'],
                    cycles_per_bit=task_info['CyclesPerBit'],
                    trans_bit_rate=task_info['TransBitRate']*5,
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

            until += env.refresh_rate

    # Continue the simulation until the last task successes/fails.
    while env.task_count < launched_task_cnt:
        until += env.refresh_rate
        try:
            env.run(until=until)
        except Exception as e:
            pass

    # Evaluation
    print("\n===============================================")
    print("Evaluation:")
    print("===============================================\n")


    m1 = SuccessRate()
    r1 = m1.eval(env.logger.task_info)
    logger.update_metric("SuccessRate", r1)

    m2 = AvgLatency()
    r2 = m2.eval(env.logger.task_info)
    logger.update_metric("AvgLatency", r2)
    
    # avg energy per
    logger.update_metric("AvgEnergy", env.avg_node_energy())
    env.close()
    
    # Stats Visualization
    vis = VisStats(logger.log_dir)
    vis.vis(env)
    
    env.close()


if __name__ == '__main__':
    main()
