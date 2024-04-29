import os
import sys

PROJECT_NAME = 'RayCloudSim'
cur_path = os.path.abspath(os.path.dirname(__file__))
root_path = cur_path
while os.path.split(os.path.split(root_path)[0])[-1] != PROJECT_NAME:
    root_path = os.path.split(root_path)[0]
root_path = os.path.split(root_path)[0]
sys.path.append(root_path)

import pandas as pd
import random

ROOT_PATH = 'eval/benchmarks/caseA/small'


def main():
    # 0. key params
    header = ['TaskName', 'GenerationTime', 'TaskID', 'TaskSize', 'CyclesPerBit', 
              'TransBitRate', 'DDL', 'SrcName']  # field names
    N, M = 500, 1000  # simulate N tasks in M time slots
    R = 19  # maximum valid node id of source nodes

    # 1. tasks
    simulated_tasks = []
    generated_time = random.choices(range(M), k=N)
    generated_time.sort()
    for i, t in enumerate(generated_time):
        simulated_tasks.append(
            [
                f't{i}',  # TaskName
                t, # GenerationTime
                i,  # TaskID
                random.randint(10, 100),  # TaskSize
                random.randint(1, 10),  # CyclesPerBit
                random.randint(20, 80),  # TransBitRate
                random.randint(50, 100),  # DDL
                f'n{random.randint(0, R)}',  # SrcName
            ]
        )
    
    # 2. saving
    filename = f"{ROOT_PATH}/tasks.csv"
    if not os.path.exists(filename):
        data = pd.DataFrame(simulated_tasks, columns=header)
        data.to_csv(filename, index=False)
    else:
        print("File already exists!")

    # 3. loading
    data = pd.read_csv(filename)
    simulated_tasks = list(data.iloc[:].values)


if __name__ == '__main__':
    main()
