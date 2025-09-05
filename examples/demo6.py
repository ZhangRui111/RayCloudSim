"""
This script demonstrates evaluation of offloading strategies.
"""

import os
import sys

current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from core.env import Env
from core.task import Task
from core.vis import *
from eval.benchmarks.caseA.small.scenario import Scenario  # testbed
from eval.metrics.metrics import SuccessRate, AvgLatency  # metric
from policies.demo.demo_random import DemoRandom  # policy


# Global statistics
net_cong_error = []
insufficient_buffer_error = []


def error_handler(error: Exception):
    """Customized error handler for different types of errors."""

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
    else:
        raise NotImplementedError(error)


def main():
    # Create the environment with the specified scenario and configuration files.
    scenario = Scenario(config_file="eval/benchmarks/caseA/small/config.json")
    env = Env(scenario, config_file="core/configs/env_config_null.json", enable_logging=True)


    # Visualization: Display the topology of the environment.
    # vis_graph(env,
    #           config_file="core/vis/configs/vis_config_base.json", 
    #           save_as="examples/vis/caseA_small.png")

    # Init the policy.
    policy = DemoRandom()

    # Begin the simulation.
    until = 1
    launched_task_cnt = 0
    timeout_task_cnt = 0
    for task_info in env.scenario.simulated_tasks:
        # Task properties:
        # ['TaskName', 'GenerationTime', 'TaskID', 'TaskSize', 'CyclesPerBit', 
        #  'TransBitRate', 'DDL', 'SrcName', 'DstName']
        generated_time = task_info[1]
        task = Task(
            id=task_info[2],
            task_size=task_info[3],
            cycles_per_bit=task_info[4],
            trans_bit_rate=task_info[5],
            ddl=task_info[6],
            src_name=task_info[7],
            task_name=task_info[0],
        )

        while True:
            # Catch completed task information.
            while env.done_task_info:
                item = env.done_task_info.pop(0)
                info = item[3]
                if not info[1]['ddl_ok']:
                    timeout_task_cnt += 1

            if env.now == generated_time:
                dst_id = policy.act(env, task)  # offloading decision
                dst_name = env.scenario.node_id2name[dst_id]
                env.process(task=task, dst_name=dst_name)
                launched_task_cnt += 1
                break

            # Execute the simulation with error handler.
            try:
                env.run(until=until)
            except Exception as e:
                error_handler(e)

            until += 1

    # Continue the simulation until the last task successes/fails.
    while env.task_count < launched_task_cnt:
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
          f"    InsufficientBufferError: {len(insufficient_buffer_error)}")

    m1 = SuccessRate()
    r1 = m1.eval(env.logger.task_info)
    print(f"\nThe success rate of all tasks: {r1:.4f}")

    print("-----------------------------------------------\n")

    print(f"There are {timeout_task_cnt} time-out tasks.")

    print("\n-----------------------------------------------")
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
# [1079.00]: Task {484}: Accomplished in Node {n14} with execution time {114.43}s
# [1133.00]: Task {479}: Accomplished in Node {n5} with execution time {112.00}s
# [1133.00]: Task {499} re-actives in Node {n5}, waiting {126.76}s
# [1133.00]: Processing Task {499} in {n5}
# [1232.00]: Task {499}: Accomplished in Node {n5} with execution time {99.00}s

# ===============================================
# Evaluation:
# ===============================================

# -----------------------------------------------
# Analysis on failed tasks:

#     NetCongestionError     : 53
#     InsufficientBufferError: 31

# The success rate of all tasks: 0.8320
# -----------------------------------------------

# There are 65 time-out tasks.

# -----------------------------------------------
# The average latency per task: 44.4626
# The average energy consumption per node: 1.2538
# -----------------------------------------------

# [1233.00]: Simulation completed!
