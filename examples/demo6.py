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


# Global statistics
net_cong_error = []
insufficient_buffer_error = []
timeout_error = []


def error_handler(error: Exception):
    """Customized error handler."""
    message = error.args[0]
    if message[0] == 'NetCongestionError':
        # Error: network congestion
        # print(message[1])
        # ----- handle this error here -----
        net_cong_error.append(message[2])
    elif message[0] == 'InsufficientBufferError':
        # Error: insufficient buffer in the destination node
        # print(message[1])
        # ----- handle this error here -----
        insufficient_buffer_error.append(message[2])
    elif message[0] == 'TimeoutError':
        # Error: the task is not executed before the deadline (ddl).
        # print(message[1])
        # ----- handle this error here -----
        timeout_error.append(message[2])
    else:
        raise NotImplementedError(error)


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
                error_handler(e)

            until += 1

    # Continue the simulation until the last task successes/fails.
    while env.process_task_cnt < len(env.scenario.simulated_tasks):
        until += 1
        try:
            env.run(until=until)
        except Exception as e:
            error_handler(e)

    # Evaluation
    print("\n===============================================")
    print("Evaluation:")
    print("===============================================\n")

    print("-----------------------------------------------")
    print(f"Analysis on failed tasks:\n\n"
          f"    NetCongestionError     : {len(net_cong_error)}\n"
          f"    InsufficientBufferError: {len(insufficient_buffer_error)}\n"
          f"    TimeoutError           : {len(timeout_error)}")

    m1 = SuccessRate()
    r1 = m1.eval(env.logger.task_info)
    print(f"\nThe success rate of all tasks: {r1:.4f}")

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
# ...
# [1015.00]: Task {499} re-actives in Node {n11}, waiting {6.34}s
# [1015.00]: Processing Task {499} in {n11}
# [1038.00]: Task {499} accomplished in Node {n11} with {23.00}s
# [1048.00]: Task {492} accomplished in Node {n15} with {35.00}s
# [1089.00]: Task {484} accomplished in Node {n10} with {115.00}s

# ===============================================
# Evaluation:
# ===============================================

# -----------------------------------------------
# Analysis on failed tasks:

#     NetCongestionError     : 48
#     InsufficientBufferError: 37
#     TimeoutError           : 22

# The success rate of all tasks: 0.7860
# -----------------------------------------------

# -----------------------------------------------
# The average latency per task: 33.2912
# The average energy consumption per node: 1221102.2975
# -----------------------------------------------

# [1090.00]: Simulation completed!
