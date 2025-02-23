import os
import sys
from tqdm import tqdm
import pandas as pd
import numpy as np

# Set up the module search path.
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from core.env import Env
from core.task import Task
from core.vis import *
from core.utils import create_log_dir   
from eval.benchmarks.Pakistan.scenario import Scenario
from eval.metrics.metrics import SuccessRate, AvgLatency
from policies.dqrl_policy import DQRLPolicy
from core.vis.plot_score import PlotScore

# Global parameters
num_epoch = 200
batch_size = 256

def run_epoch(env: Env, policy, data: pd.DataFrame, refresh_rate=1, train=True):
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
    last_task_id = None
    until = 0
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
        
        print(env.logger.node_info  )

        # Wait until the simulation reaches the task's generation time.
        while True:
            while env.done_task_info:
                env.done_task_info.pop(0)
            if env.now >= generated_time:
                # Get action and current state from the policy.
                action, state = policy.act(env, task)
                dst_name = env.scenario.node_id2name[action]
                env.process(task=task, dst_name=dst_name)

                # Update previous transition with the new state's observation.
                if last_task_id is not None:
                    prev_state, prev_action, _ = stored_transitions[last_task_id]
                    stored_transitions[last_task_id] = (prev_state, prev_action, state)
                break
            try:
                env.run(until=until)
            except Exception:
                pass
            until += refresh_rate

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
    while env.process_task_cnt < len(data):
        until += refresh_rate
        try:
            env.run(until=until)
        except Exception:
            pass
    return env

def create_env(scenario):
    """Create and return an environment instance."""
    return Env(scenario, config_file="core/configs/env_config_null.json", refresh_rate=1, verbose=False)


def main():
    flag = 'Tuple30K'
    refresh_rate = 0.001  # Simulation time refresh rate
    scenario = Scenario(config_file=f"eval/benchmarks/Pakistan/data/{flag}/config.json", flag=flag)
    
    # Load train and test datasets.
    train_data = pd.read_csv(f"eval/benchmarks/Pakistan/data/{flag}/trainset.csv")
    test_data = pd.read_csv(f"eval/benchmarks/Pakistan/data/{flag}/testset.csv")
    
    log_dir = create_log_dir("DQRL", flag=flag, num_epoch=num_epoch, batch_size=batch_size)
    
    
    
    # Initialize the policy.
    env = create_env(scenario)
    policy = DQRLPolicy(env=env, lr=1e-3)
    
    m1 = SuccessRate()
    m2 = AvgLatency()
    
    plotter = PlotScore(metrics=['SuccessRate', 'AvgLatency'], modes=['Training', 'Testing'], save_dir=log_dir)
    
    for epoch in range(num_epoch):
        print(f"Epoch {epoch+1}/{num_epoch}")
        
        # Training phase.
        env = create_env(scenario)
        env = run_epoch(env, policy, train_data, refresh_rate=refresh_rate, train=True)
        print(f"Training - AvgLatency: {m2.eval(env.logger.task_info):.4f}, SuccessRate: {m1.eval(env.logger.task_info):.4f}")
        plotter.append(mode='Training', metric='SuccessRate', value=m1.eval(env.logger.task_info))
        plotter.append(mode='Training', metric='AvgLatency', value=m2.eval(env.logger.task_info))
        env.close()
        
        # Testing phase.
        env = create_env(scenario)
        env = run_epoch(env, policy, test_data, refresh_rate=refresh_rate, train=False)
        print(f"Testing  - AvgLatency: {m2.eval(env.logger.task_info):.4f}, SuccessRate: {m1.eval(env.logger.task_info):.4f}")
        print("===============================================")
        plotter.append(mode='Testing', metric='SuccessRate', value=m1.eval(env.logger.task_info))
        plotter.append(mode='Testing', metric='AvgLatency', value=m2.eval(env.logger.task_info))
        env.close()
        
    plotter.plot(num_epoch)

if __name__ == '__main__':
    main()
