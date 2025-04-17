"""
This script demonstrates how to run the DQRLPolicy.

Oh, wait a moment. It seems that extra effort is required to make this method work. The current version 
is for reference only, and contributions are welcome.
"""

import os
import sys
import random

random.seed(42)

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
from core.vis.logger import Logger
from eval.benchmarks.Pakistan.scenario import Scenario
from eval.metrics.metrics import SuccessRate, AvgLatency
from policies.dqrl_policy import DQRLPolicy

def run_epoch(config, policy, data: pd.DataFrame, train=True, lambda_=(1, 1, 1
                                                                       )):
    """
    Run one simulation epoch over the provided task data.
    lambda_ = (fail penality, time, energy) if time is more important than energy, then lambda_ = (_, 1, 0) and vice versa.

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
    
    env = create_env(config)
    
    until = 0
    launched_task_cnt = 0
    last_task_id = None
    pbar = tqdm(data.iterrows(), total=len(data))
    stored_transitions = {}
    number_in_batch = config["training"]["batch_size"]
    
    max_total_time = 0
    max_total_energy = 0
    
    for i, task_info in pbar:
        generated_time = task_info['GenerationTime']
        task = Task(task_id=task_info['TaskID'],
                    task_size=task_info['TaskSize'],
                    cycles_per_bit=task_info['CyclesPerBit'],
                    trans_bit_rate=task_info['TransBitRate'],
                    ddl=task_info['DDL'] ,
                    src_name='e0',
                    task_name=task_info['TaskName'])

        # Wait until the simulation reaches the task's generation time.
        while True:
            while env.done_task_info:
                item = env.done_task_info.pop(0)
            
            if env.now >= generated_time:
                # Get action and current state from the policy.
                action, state = policy.act(env, task, train=train)
                dst_name = env.scenario.node_id2name[action]
                env.process(task=task, dst_name=dst_name)
                launched_task_cnt += 1
                number_in_batch -= 1

                # Update previous transition with the new state's observation.
                if last_task_id is not None and train:
                    prev_state, prev_action, _ = stored_transitions[last_task_id]
                    stored_transitions[last_task_id] = (prev_state, prev_action, state)
                
                break
            
            until += env.refresh_rate
            
            try:
                env.run(until=until)
            except Exception as e:
                pass
            
        if train:
            done = False  # Each task is treated as an individual episode.
            last_task_id = task.task_id
            stored_transitions[last_task_id] = (state, action, None)
            
            # Process stored transitions if the task has been completed.
            for task_id, (state, action, next_state) in list(stored_transitions.items()):
                if task_id in env.logger.task_info:
                    val = env.logger.task_info[task_id]
                    if val[0] == 0:
                        task_trans_time, task_wait_time, task_exe_time = val[2]
                        total_time = task_trans_time + task_wait_time + task_exe_time
                        task_trans_energy, task_exe_energy = val[3]
                        total_energy = task_trans_energy + task_exe_energy
                        max_total_time = max(max_total_time, total_time)
                        max_total_energy = max(max_total_energy, total_energy)
                        reward = - ((lambda_[1] * total_time/max_total_time) + (lambda_[2] * total_energy/max_total_energy))
                    else:
                        reward = -lambda_[0]
                    policy.store_transition(state, action, reward, next_state, done)
                    del stored_transitions[task_id]
            # Update the policy every batch_size tasks during training.
            if number_in_batch < 1:
                r1 = m1.eval(env.logger)
                r2 = m2.eval(env.logger)
                e = env.avg_node_energy(power=True)
                pbar.set_postfix({"SR": f"{r1:.3f}", "L": f"{r2:.3f}", "E": f"{e:.3f}"})
                policy.update()
                number_in_batch = random.randint(config["training"]["batch_size"]//2, config["training"]["batch_size"]) # Batch siize ramdomization. (Acoid the same batch splitting)
                


    # Continue simulation until all tasks are processed.
    while env.task_count < launched_task_cnt:
        until += env.refresh_rate
        try:
            env.run(until=until)
        except Exception as e:
            pass
    
    return env


def create_env(config):
    """Create and return an environment instance."""
    dataset = config["env"]["dataset"]
    flag = config["env"]["flag"]
    scenario = Scenario(config_file=f"eval/benchmarks/{dataset}/data/{flag}/config.json", flag=flag)
    env = Env(scenario, config_file="core/configs/env_config_null.json", verbose=False)
    env.refresh_rate = config['env']['refresh_rate']
    return env



def main():
    config = {
        "policy": "DQRL",
        "env": {
            "dataset": "Pakistan",
            "flag": "Tuple30K",
            "refresh_rate": 0.001
        },
        "training": {
            "num_epochs": 10,
            "batch_size": 256,
            "lr": 0.001,
            "lr_decay": 0.9,
            "gamma": 0.2,
            "epsilon": 0.1,
            "epsilon_decay": 0.8,
            "lambda": [
            1e6,
            1,
            0
            ]
        },
        "model": {
            "d_model": 128,
            "n_layers": 3,
            "obs_type": [
            "cpu",
            "bw",
            "buffer"
            ]
        }
        }
    
    
    logger = Logger(config)
    

    env = create_env(config)
    
    # Load train and test datasets.
    train_data = pd.read_csv(f"eval/benchmarks/Pakistan/data/{config['env']['flag']}/trainset.csv")
    test_data = pd.read_csv(f"eval/benchmarks/Pakistan/data/{config['env']['flag']}/testset.csv")

    # Initialize the policy.
    policy = DQRLPolicy(env=env, config=config)
    
    m1 = SuccessRate()
    m2 = AvgLatency()
    
    
    for epoch in range(config["training"]["num_epochs"]):
        
        logger.update_epoch(epoch)

        env.close()
        # Training phase.
        
        logger.update_mode('Training')
        
        env = run_epoch(config, policy, train_data, train=True, lambda_=config["training"]["lambda"])

        
        logger.update_metric('SuccessRate', m1.eval(env.logger))
        logger.update_metric('AvgLatency', m2.eval(env.logger))
        logger.update_metric('AvgPower', env.avg_node_energy(power=True))
        
        env.close()
        
        # Testing phase.
        
        logger.update_mode('Testing')
        
        env = run_epoch(config, policy, test_data, train=False)
        
        logger.update_metric('SuccessRate', m1.eval(env.logger))
        logger.update_metric('AvgLatency', m2.eval(env.logger))
        logger.update_metric('AvgPower', env.avg_node_energy(power=True))
        
        policy.epsilon_decay(config["training"]["epsilon_decay"])
        policy.lr_decay(config["training"]["lr_decay"])
        env.close()

    logger.plot()
    logger.save_csv()
    
    vis_stats = VisStats(save_path=logger.log_dir)
    vis_stats.vis(env)
    
    logger.close()


if __name__ == '__main__':
    main()
