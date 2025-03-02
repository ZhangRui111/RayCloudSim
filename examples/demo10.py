"""
This script demonstrates how to run the DQRLPolicy.

Oh, wait a moment. It seems that extra effort is required to make this method work. The current version 
is for reference only, and contributions are welcome.
"""

import os
import sys

current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

import pandas as pd
from tqdm import tqdm

from core.env import Env
from core.task import Task
from core.vis import *
from core.vis.vis_stats import VisStats
from eval.benchmarks.Pakistan.scenario import Scenario
from eval.metrics.metrics import SuccessRate, AvgLatency
from policies.dqrl_policy import DQRLPolicy
from core.vis.plot_score import PlotScore


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


# Global parameters
num_epoch = 50
batch_size = 256


def run_epoch(env: Env, policy, data: pd.DataFrame, train=True):
    """
    Run one simulation epoch over the provided task data.

    For each task:
      - Wait until the task's generation time.
      - Obtain the current state and select an action via the policy.
      - Schedule the task for processing.
      - Once processed, record the next state and compute the reward.
      - Store the transition for policy training.
      
    Every 'batch_size' tasks, update the policy.
    """
    m1 = SuccessRate()
    m2 = AvgLatency()
    
    until = 0
    launched_task_cnt = 0
    last_task_id = None
    pbar = tqdm(data.iterrows(), total=len(data))
    stored_transitions = {}
    for i, task_info in pbar:
        generated_time = task_info['GenerationTime']
        task = Task(task_id=task_info['TaskID'],
                    task_size=task_info['TaskSize'],
                    cycles_per_bit=task_info['CyclesPerBit'],
                    trans_bit_rate=task_info['TransBitRate'],
                    ddl=task_info['DDL'],
                    src_name='e0',
                    task_name=task_info['TaskName'])

        # Wait until the simulation reaches the task's generation time.
        while True:
            while env.done_task_info:
                item = env.done_task_info.pop(0)
            
            if env.now >= generated_time:
                # Get action and current state from the policy.
                action, state = policy.act(env, task)
                dst_name = env.scenario.node_id2name[action]
                env.process(task=task, dst_name=dst_name)
                launched_task_cnt += 1

                # Update previous transition with the new state's observation.
                if last_task_id is not None:
                    prev_state, prev_action, _ = stored_transitions[last_task_id]
                    stored_transitions[last_task_id] = (prev_state, prev_action, state)
                
                break
            
            try:
                env.run(until=until)
            except Exception:
                pass

            until += 1

        done = True  # Each task is treated as an individual episode.
        last_task_id = task.task_id
        stored_transitions[last_task_id] = (state, action, None)
        
        # print(env.logger.task_info)

        # Process stored transitions if the task has been completed.
        for task_id, (state, action, next_state) in list(stored_transitions.items()):
            if task_id in env.logger.task_info:
                val = env.logger.task_info[task_id]
                if val[0] == 0:
                    task_trans_time, task_wait_time, task_exe_time = val[1]
                    total_time = task_trans_time + task_wait_time + task_exe_time
                    reward = -total_time
                else:
                    reward = -1e6
                policy.store_transition(state, action, reward, next_state, done)
                del stored_transitions[task_id]

        # Update the policy every batch_size tasks during training.
        if (i + 1) % batch_size == 0 and train:
            r1 = m1.eval(env.logger.task_info)
            r2 = m2.eval(env.logger.task_info)
            pbar.set_postfix({"AvgLatency": f"{r2:.3f}", "SuccessRate": f"{r1:.3f}"})
            policy.update()

    # Continue simulation until all tasks are processed.
    while env.task_count < launched_task_cnt:
        until += 1
        try:
            env.run(until=until)
        except Exception:
            pass
    
    return env


def create_env(scenario):
    """Create and return an environment instance."""
    return Env(scenario, config_file="core/configs/env_config_null.json", verbose=False)


def main():
    flag = 'Tuple30K'

    scenario = Scenario(config_file=f"eval/benchmarks/Pakistan/data/{flag}/config.json", flag=flag)
    env = create_env(scenario)
    
    # Load train and test datasets.
    train_data = pd.read_csv(f"eval/benchmarks/Pakistan/data/{flag}/trainset.csv")
    test_data = pd.read_csv(f"eval/benchmarks/Pakistan/data/{flag}/testset.csv")
    
    log_dir = create_log_dir("vis/DQRL", flag=flag, num_epoch=num_epoch, batch_size=batch_size)
    
    # Initialize the policy.
    policy = DQRLPolicy(env=env, lr=1e-4)
    
    m1 = SuccessRate()
    m2 = AvgLatency()
    
    plotter = PlotScore(metrics=['SuccessRate', 'AvgLatency'], 
                        modes=['Training', 'Testing'], save_dir=log_dir)
    
    for epoch in range(num_epoch):
        print(f"Epoch {epoch+1}/{num_epoch}")
        
        # Training phase.
        env = create_env(scenario)
        env = run_epoch(env, policy, train_data, train=True)
        print(f"Training - AvgLatency: {m2.eval(env.logger.task_info):.4f}, " 
              f"SuccessRate: {m1.eval(env.logger.task_info):.4f}")
        plotter.append(mode='Training', metric='SuccessRate', value=m1.eval(env.logger.task_info))
        plotter.append(mode='Training', metric='AvgLatency', value=m2.eval(env.logger.task_info))
        env.close()
        
        # Testing phase.
        env = create_env(scenario)
        env = run_epoch(env, policy, test_data, train=False)
        print(f"Testing  - AvgLatency: {m2.eval(env.logger.task_info):.4f}, " 
              f"SuccessRate: {m1.eval(env.logger.task_info):.4f}")
        print("===============================================")
        plotter.append(mode='Testing', metric='SuccessRate', value=m1.eval(env.logger.task_info))
        plotter.append(mode='Testing', metric='AvgLatency', value=m2.eval(env.logger.task_info))
        env.close()
        
    
    # Final testing phase.
    print("Final Testing Phase")
    env = create_env(scenario)
    env = run_epoch(env, policy, test_data, train=False)
    print(f"Testing  - AvgLatency: {m2.eval(env.logger.task_info):.4f}, " 
          f"SuccessRate: {m1.eval(env.logger.task_info):.4f}")
    env.close()
    
    vis_stats = VisStats(save_path=log_dir)
    vis_stats.vis(env)

    plotter.plot(num_epoch)

if __name__ == '__main__':
    main()
