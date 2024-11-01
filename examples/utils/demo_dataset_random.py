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


def main():
    # 0. key params
    header = ['TaskName', 'GenerationTime', 'TaskID', 'TaskSize', 'CyclesPerBit', 
              'TransBitRate', 'DDL', 'SrcName', 'DstName']  # field names
    N, M = 400, 1000  # simulate N tasks in M time slots
    R = 9  # maximum valid node id of source nodes

    # 1. tasks
    simulated_tasks = []
    generated_time = random.choices(range(M), k=N)
    generated_time.sort()
    for i, t in enumerate(generated_time):
        simulated_tasks.append(
            [
                f't{i}', # TaskName
                t, # GenerationTime
                i,  # TaskID
                random.randint(10, 100),  # TaskSize
                random.randint(1, 10),  # CyclesPerBit
                random.randint(20, 80),  # TransBitRate
                random.randint(50, 100),  # DDL
                f'n{random.randint(0, R)}',  # SrcName
                f'n{random.randint(0, R)}',  # DstName
            ]
        )
    
    # 2. saving
    filename = "examples/dataset/demo3_dataset.csv"
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


# def main():
#     # 1. tasks
#     generated_time = random.choices(range(1000), k=400)
#     generated_time.sort()
#     simulated_tasks = []
#     for i, t in enumerate(generated_time):
#         simulated_tasks.append(
#             (t, # generated_time
#              [i,  # task_id
#               random.randint(10, 100),  # task_size
#               random.randint(1, 10),  # cycles_per_bit
#               random.randint(20, 80),  # trans_bit_rate
#               random.randint(50, 100),  # ddl
#               f'n{random.randint(0, 9)}',  # src_name
#               f't{i}'], # task_name
#               f'n{random.randint(0, 9)}')  # dst_name
#         )
    
#     # 2. saving
#     if not os.path.exists("examples/utils/demo3_dataset.txt"):
#         with open("examples/utils/demo3_dataset.txt", 'w+') as fw:
#             fw.write(str(simulated_tasks))
#     else:
#         print("File already exists!")

#     # 3. loading
#     with open("examples/utils/demo3_dataset.txt", 'r') as fr:
#         simulated_tasks = eval(fr.read())
