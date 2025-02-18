import os
import sys
from tqdm import tqdm
import time
import pandas as pd
import numpy as np

current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from core.env import Env
from core.task import Task
from core.vis import *

from eval.benchmarks.Pakistan.scenario import Scenario
from eval.metrics.metrics import SuccessRate, AvgLatency  # metric
from policies.dqrl_policy import DQRLPolicy  # use the DQRLPolicy defined above

num_epoch = 10
batch_size = 64

def run_epoch(env, policy, data, refresh_rate=1, train=True):
    """
    Runs one epoch of simulation.
    
    For each task in the dataset:
      - Wait until the task's generated time is reached.
      - Get the current state and choose an action.
      - Schedule the task on the chosen destination.
      - After the task is processed, record the next state.
      - Compute the reward (e.g. using average latency from metrics).
      - Store the transition.
      
    Every batch_size tasks, perform an update.
    """
    m1 = SuccessRate()
    m2 = AvgLatency()
            
    last_task_id = None
    until = 0
    pbar = tqdm(data.iterrows(), total=len(data))
    
    stored_transitions = {}
    
    for i, task_info in pbar:

        # Example header: ['TaskName', 'GenerationTime', 'TaskID', 'TaskSize', 'CyclesPerBit', 'TransBitRate', 'DDL']
        generated_time = task_info['GenerationTime']
        task = Task(task_id=task_info['TaskID'],
                    task_size=task_info['TaskSize'],
                    cycles_per_bit=task_info['CyclesPerBit'],
                    trans_bit_rate=task_info['TransBitRate'],
                    ddl=task_info['DDL'],
                    src_name='e0',
                    task_name=task_info['TaskName'])

        # Wait until current simulation time (env.now) is close to generated_time.
        while True:
            # Process any completed tasks.
            while env.done_task_info:
                env.done_task_info.pop(0)
            
            if env.now >= generated_time:
                # Capture state before acting.
                action, state = policy.act(env, task)
                dst_name = env.scenario.node_id2name[action]
                env.process(task=task, dst_name=dst_name)
                if last_task_id is not None:
                    stored_transitions[last_task_id] = (stored_transitions[last_task_id][0], stored_transitions[last_task_id][1], state)
                
                break
            try:
                env.run(until=until)
            except Exception as e:
                pass

            until += refresh_rate
        
        # next_state = policy._make_observation(env, task)
        # For demonstration, we use the average latency (r2) as the reward.
        # (In practice you might use a different reward function.)
        
        done = True  # we treat each task as an individual episode
        
        last_task_id = task.task_id
        
        stored_transitions[last_task_id] = (state, action, None)
        
        items = list(stored_transitions.items())
        
        for task_id, (state, action, next_state) in items:
            
            if task_id in env.logger.task_info:
                
                val = env.logger.task_info[task_id]
                
                if val[0] == 0:
                    
                    task_trans_time, task_wait_time, task_exe_time = val[1][0], val[1][1], val[1][2]
                    
                    total_time = task_wait_time + task_exe_time + task_trans_time
                    
                    # reward = np.exp(-(task_wait_time + task_exe_time + task_trans_time))
                    reward = -total_time
                    
                else:
                    reward = -1e6
                    
                policy.store_transition(state, action, reward, next_state, done)
                
                del stored_transitions[task_id]

            
        if (i + 1) % batch_size == 0 and train:
            r1 = m1.eval(env.logger.task_info)
            r2 = m2.eval(env.logger.task_info)
            pbar.set_postfix({"AvgLatency": f"{r2:.3f}", "SuccessRate": f"{r1:.3f}"})
            
            loss = policy.update()
            
            # Optionally, print the loss.
    # Continue simulation until all tasks are processed.
    while env.process_task_cnt < len(data):
        until += refresh_rate
        try:
            env.run(until=until)
        except Exception as e:
            pass
    
    return env

def create_env(scenario):
    # You can adjust the refresh_rate (in seconds) as needed.
    env = Env(scenario, config_file="core/configs/env_config_null.json", refresh_rate=1, verbose=False)
    return env
    
def main():
    flag = 'Tuple30K'
    refresh_rate = 0.001  # You can choose a different refresh_rate here.
    
    scenario = Scenario(config_file=f"eval/benchmarks/Pakistan/data/{flag}/config.json", flag=flag)
    env = create_env(scenario)
    
    test_data = pd.read_csv(f"eval/benchmarks/Pakistan/data/{flag}/testset.csv")
    train_data = pd.read_csv(f"eval/benchmarks/Pakistan/data/{flag}/trainset.csv")
    
    policy = DQRLPolicy(env=env, lr=1e-3)
    
    m1 = SuccessRate()
    m2 = AvgLatency()
    
    for epoch in range(num_epoch):
        print(f"Epoch {epoch+1}/{num_epoch}")
        
        env = create_env(scenario)
        env = run_epoch(env, policy, train_data, refresh_rate=refresh_rate, train=True)
        
        r2 = m2.eval(env.logger.task_info)
        print(f"Training: The average latency per task: {r2:.4f}")
        print(f"Training: The success rate of all tasks: {m1.eval(env.logger.task_info):.4f}")
        env.close()
        
        env = create_env(scenario)
        env = run_epoch(env, policy, test_data, refresh_rate=refresh_rate, train=False)
        r2 = m2.eval(env.logger.task_info)
        r1 = m1.eval(env.logger.task_info)
        print(f"Testing: The average latency per task: {r2:.4f}")
        print(f"Testing: The success rate of all tasks: {r1:.4f}")
        print("===============================================")
        env.close()

if __name__ == '__main__':
    main()
