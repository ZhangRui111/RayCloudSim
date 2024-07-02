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
from core.vis import *

from eval.benchmarks.caseA.small.scenario import Scenario  # testbed
from eval.metrics.metrics import SuccessRate, AvgLatency  # metric
from policies.demo.demo_random import DemoRandom  # policy


def main():
    # Init the Env
    scenario=Scenario(config_file="eval/benchmarks/caseA/small/config.json")
    env = Env(scenario, config_file="core/configs/env_config_null.json")
    
    # # Visualization: the topology
    # vis_graph(env,
    #           config_file="core/vis/configs/vis_config_base.json", 
    #           save_as="examples/vis/caseA_small.png")

    # Init the policy
    policy = DemoRandom()

    # Begin Simulation
    until = 1
    for task_info in env.scenario.simulated_tasks:
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


# # ==================== Simulation log ====================
# ...
# [1048.00]: Task {498} accomplished in Node {n19} with {2.00}s
# [1055.00]: Task {480} accomplished in Node {n14} with {25.00}s
# [1055.00]: **TimeoutError: Task {487}** timeout in Node {n14}
# [1090.00]: Task {496} accomplished in Node {n16} with {62.00}s
# [1090.00]: **TimeoutError: Task {499}** timeout in Node {n16}

# -----------------------------------------------
# Evaluation:

# The success rate of all tasks: 0.792
# The average latency per task: 34.447
# -----------------------------------------------

# [1090.00]: Simulation completed!
