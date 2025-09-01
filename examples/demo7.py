"""
This script demonstrates the node online/offline functionality.
"""

import os
import sys

# Add the parent directory to sys.path for module import.
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from core.env import Env
from core.task import Task
from core.vis import *
from examples.scenarios.scenario_1 import Scenario


def main():
    # Create the environment with the specified scenario and configuration files.
    scenario = Scenario(config_file="examples/scenarios/configs/config_3.json")
    env = Env(scenario, config_file="core/configs/env_config_null.json")
    
    # ========== Node online/offline without running/pending tasks ==========
    # Launch a task
    task = Task(
        id=0,
        task_size=20,
        cycles_per_bit=10,
        trans_bit_rate=20,
        src_name='n5',
    )
    env.process(task=task, dst_name='n9')  # n5 => n0 => n1 => n9
    env.run(until=25)

    # Take Node n1 offline
    env.take_node_offline("n1")

    # Launch a new task
    task = Task(
        id=1,
        task_size=20,
        cycles_per_bit=10,
        trans_bit_rate=20,
        src_name='n5',
    )
    env.process(task=task, dst_name='n9')  # routing path changed, n5 => n4 => n3 => n9
    env.run(until=50)

    # Bring Node n10 online
    env.bring_node_online(
        info={
            "node_info": {
                "NodeType": "Node",
                "NodeName": "n10",
                "NodeId": 10,
                "MaxCpuFreq": 20,
                "MaxBufferSize": 285,
                "LocX": 40,
                "LocY": 60,
                "IdleEnergyCoef": 0.01,
                "ExeEnergyCoef": 0.1
            },
            "link_info": [
                {"EdgeType": "Link", "SrcNodeID": 5, "DstNodeID": 10, "Bandwidth": 100},
                {"EdgeType": "Link", "SrcNodeID": 9, "DstNodeID": 10, "Bandwidth": 100},
            ]
        }
    )

    # Launch a new task
    task = Task(
        id=2,
        task_size=20,
        cycles_per_bit=10,
        trans_bit_rate=20,
        src_name='n5',
    )
    env.process(task=task, dst_name='n9')  # routing path changed, n5 => n10 => n9
    env.run(until=70)

    # ========== Node online/offline with running/pending tasks ==========
    # Launch two new tasks
    task = Task(
        id=3,
        task_size=100,
        cycles_per_bit=10,
        trans_bit_rate=20,
        src_name='n5',
    )
    env.process(task=task, dst_name='n9')

    task = Task(
        id=4,
        task_size=100,
        cycles_per_bit=10,
        trans_bit_rate=20,
        src_name='n4',
    )
    env.process(task=task, dst_name='n9')

    env.run(until=90)

    # Take Node n9 offline
    env.take_node_offline("n9")

    env.run(until=100)

    # ========== Node online/offline with transmitting tasks ==========
    # Launch two new tasks
    task = Task(
        id=5,
        task_size=100,
        cycles_per_bit=10,
        trans_bit_rate=20,
        src_name='n5',
    )
    env.process(task=task, dst_name='n3')

    env.run(until=105)

    # Take Node n3 offline
    env.take_node_offline("n3")

    env.run(until=300)

    # Close the environment after simulation.
    env.close()


if __name__ == '__main__':
    main()


# # ==================== Simulation log ====================
# [0.00]: Task {0} generated in Node {n5}
# [0.00]: Task {0}: {n5} --> {n9}
# [3.00]: Task {0} arrived Node {n9} with {3.00}s
# [3.00]: Processing Task {0} in {n9}
# [20.00]: Task {0}: Completed in Node {n9} with execution time {16.67}s

# [25.00]: ***WARNING*** Node {1} has gone offline.

# [25.00]: Task {1} generated in Node {n5}
# [25.00]: Task {1}: {n5} --> {n9}
# [28.00]: Task {1} arrived Node {n9} with {3.00}s
# [28.00]: Processing Task {1} in {n9}
# [45.00]: Task {1}: Completed in Node {n9} with execution time {16.67}s

# [50.00]: ***WARNING*** Node 10 has come online.

# [50.00]: Task {2} generated in Node {n5}
# [50.00]: Task {2}: {n5} --> {n9}
# [52.00]: Task {2} arrived Node {n9} with {2.00}s
# [52.00]: Processing Task {2} in {n9}
# [69.00]: Task {2}: Completed in Node {n9} with execution time {16.67}s
# [70.00]: Task {3} generated in Node {n5}
# [70.00]: Task {3}: {n5} --> {n9}
# [70.00]: Task {4} generated in Node {n4}
# [70.00]: Task {4}: {n4} --> {n9}
# [80.00]: Task {3} arrived Node {n9} with {10.00}s
# [80.00]: Processing Task {3} in {n9}
# [80.00]: Task {4} arrived Node {n9} with {10.00}s
# [80.00]: Task {4} is buffered in Node {n9}
# [90.00]: Task 3 is terminated abnormally (Node 9 has gone offline).
# [90.00]: Task 4 is terminated abnormally (Node 9 has gone offline).

# [90.00]: ***WARNING*** Node {9} has gone offline.

# [100.00]: Task {5} generated in Node {n5}
# [100.00]: Task {5}: {n5} --> {n3}
# [105.00]: Task 5's transmission was abnormally terminated (Destination Node 3 has gone offline).

# [105.00]: ***WARNING*** Node {3} has gone offline.

# [300.00]: Simulation completed!
