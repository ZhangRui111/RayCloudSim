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
from eval.benchmarks.Pakistan.scenario import Scenario
from eval.metrics.metrics import SuccessRate, AvgLatency  # metric
from policies.demo.demo_round_robin import DemoRoundRobin


def main():
    flag = 'Tuple30K'
    # flag = 'Tuple50K'
    # flag = 'Tuple100K'
    
    # Create the environment with the specified scenario and configuration files.
    scenario=Scenario(config_file=f"eval/benchmarks/Pakistan/data/{flag}/config.json", flag=flag)
    env = Env(scenario, config_file="core/configs/env_config_null.json", enable_logging=True)

    # Load the test dataset.
    data = pd.read_csv(f"eval/benchmarks/Pakistan/data/{flag}/testset.csv")

    # Init the policy.
    policy = DemoRoundRobin()

    # Begin the simulation.
    until = 0
    launched_task_cnt = 0
    for i, task_info in data.iterrows():
        generated_time = task_info['GenerationTime']
        task = Task(
            id=task_info['TaskID'],
            task_size=task_info['TaskSize'],
            cycles_per_bit=task_info['CyclesPerBit'],
            trans_bit_rate=task_info['TransBitRate'],
            ddl=task_info['DDL'],
            src_name='e0',
            task_name=task_info['TaskName'],
        )

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


if __name__ == '__main__':
    main()


# # ==================== Simulation log ====================
# [1263.00]: Processing Task {8967} in {e0}
# [1265.00]: Task {8967}: Accomplished in Node {e0} with execution time {1.70}s
# [1265.00]: Task {8983} re-actives in Node {e0}, waiting {127.17}s
# [1265.00]: Processing Task {8983} in {e0}
# [1266.00]: Task {8983}: Accomplished in Node {e0} with execution time {0.90}s

# ===============================================
# Evaluation:
# ===============================================

# -----------------------------------------------
# The success rate of all tasks: 0.7120
# -----------------------------------------------

# -----------------------------------------------
# The average latency per task: 61.3618
# The average energy consumption per node: 5311811210625.0000
# -----------------------------------------------

# [1267.00]: Simulation completed!
