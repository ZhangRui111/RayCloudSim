"""
This script demonstrates how to simulate multiple epochs.
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
    env = Env(scenario, config_file="core/configs/env_config_null.json", enable_logging=False)

    # Load simulated tasks from the CSV dataset.
    data = pd.read_csv("examples/dataset/demo3_dataset.csv")
    simulated_tasks = list(data.iloc[:].values)
    n_tasks = len(simulated_tasks)

    # Begin the simulation.
    until = 1
    for i_epoch in range(3):  # multiple epoch

        env.reset()
        base_until = until
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

                if env.now - base_until == generated_time:
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
        print(f"\nEpoch {i_epoch}:")
        analyze_simulation_result(env.logger.task_info)

    env.close()


if __name__ == '__main__':
    main()


# # ==================== Simulation log ====================
# Epoch 0:

# -----------------------------------------------
# Done simulation!
# Success Rate: 64.00%, i.e., 256/400

# NetworkXNoPathError    : 0
# NetCongestionError     : 6
# InsufficientBufferError: 70
# NodeOfflineError       : 0
# NodeNotFoundError      : 0
# TimeoutError           : 68
# -----------------------------------------------


# Epoch 1:

# -----------------------------------------------
# Done simulation!
# Success Rate: 64.00%, i.e., 256/400

# NetworkXNoPathError    : 0
# NetCongestionError     : 6
# InsufficientBufferError: 70
# NodeOfflineError       : 0
# NodeNotFoundError      : 0
# TimeoutError           : 68
# -----------------------------------------------


# Epoch 2:

# -----------------------------------------------
# Done simulation!
# Success Rate: 64.00%, i.e., 256/400

# NetworkXNoPathError    : 0
# NetCongestionError     : 6
# InsufficientBufferError: 70
# NodeOfflineError       : 0
# NodeNotFoundError      : 0
# TimeoutError           : 68
# -----------------------------------------------
