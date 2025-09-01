"""
This script demonstrates error handling for common network and task issues.
"""

import os
import sys

current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

import pandas as pd
import random

from core.env import Env
from core.task import Task
from core.code import *
from core.utils import analyze_simulation_result
from examples.scenarios.scenario_3 import Scenario


def error_handler(error: Exception):
    """Customized error handler."""
    message = error.args[0]
    task_id, code, info = message
    # ----- handle error -----
    return


def main():
    # Create the environment with the specified scenario and configuration files.
    scenario = Scenario(config_file="examples/scenarios/configs/config_3.json")
    env = Env(scenario, config_file="core/configs/env_config_null.json")

    # Load simulated tasks from the CSV dataset.
    data = pd.read_csv("examples/dataset/demo3_dataset.csv")
    simulated_tasks = list(data.iloc[:].values)

    # Begin the simulation.
    until = 1
    launched_task_cnt = 0
    for task_info in simulated_tasks:
        # Task properties:
        # ['TaskName', 'GenerationTime', 'TaskID', 'TaskSize', 'CyclesPerBit', 
        #  'TransBitRate', 'DDL', 'SrcName', 'DstName']
        generated_time, dst_name = task_info[1], task_info[8]

        while True:
            # Catch completed task information.
            while env.done_task_info:
                item = env.done_task_info.pop(0)

            if abs(env.now - generated_time) < 1e-6:
                # Manually avoid the situation where the source node is not found.
                if task_info[7] not in env.scenario.node_id2name.values():
                    task_info[7] = random.choice(list(env.scenario.node_id2name.values()))

                task = Task(
                    id=task_info[2],
                    task_size=task_info[3],
                    cycles_per_bit=task_info[4],
                    trans_bit_rate=task_info[5],
                    ddl=task_info[6],
                    src_name=task_info[7],
                    task_name=task_info[0],
                )

                env.process(task=task, dst_name=dst_name)
                launched_task_cnt += 1
                break
            
            # Take node "n9" offline.
            if abs(env.now - 500) < 1e-6:
                env.take_node_offline("n9")

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
    
    # Simulation result analysis.
    analyze_simulation_result(env.logger.task_info)

    env.close()


if __name__ == '__main__':
    main()


# # ==================== Simulation log ====================
# ...
# [1178.00]: Processing Task {369} in {n8}
# [1208.00]: Task {369}: Completed in Node {n8} with execution time {30.00}s
# [1208.00]: Task {376} re-actives in Node {n8}, waiting {269.65}s
# [1208.00]: Processing Task {376} in {n8}
# [1318.00]: Task {376}: Completed in Node {n8} with execution time {109.80}s

# -----------------------------------------------
# Done simulation!
# Success Rate: 59.50%, i.e., 238/400

# NetworkXNoPathError    : 0
# NetCongestionError     : 5
# InsufficientBufferError: 68
# NodeOfflineError       : 2
# NodeNotFoundError      : 22
# TimeoutError           : 65
# -----------------------------------------------

# [1319.00]: Simulation completed!
