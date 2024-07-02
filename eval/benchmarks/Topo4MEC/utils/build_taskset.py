import os
import sys

PROJECT_NAME = 'RayCloudSim'
cur_path = os.path.abspath(os.path.dirname(__file__))
root_path = cur_path
while os.path.split(os.path.split(root_path)[0])[-1] != PROJECT_NAME:
    root_path = os.path.split(root_path)[0]
root_path = os.path.split(root_path)[0]
sys.path.append(root_path)

import json
import numpy as np
import pandas as pd


def main():
    # 1. loading source files
    flag, num_arrivals_per_ingress = '25N50E', 200
    # flag, num_arrivals_per_ingress = '50N50E', 200
    # flag, num_arrivals_per_ingress = '100N150E', 200 
    # flag, num_arrivals_per_ingress = 'MilanCityCenter', 200
    with open(f"eval/benchmarks/Topo4MEC/source/{flag}/ingress.txt", 'r') as f:
        ingress_line = f.readlines()[1].split()
        ingress_line = [int(item) - 1 for item in ingress_line]  # RayCloudSim is 0-index
    save_as = f"eval/benchmarks/Topo4MEC/data/{flag}/tasks.csv"
    params_save_as = f"eval/benchmarks/Topo4MEC/data/{flag}/task_configs.json"

    # 2. parameters
    header = ['TaskName', 'GenerationTime', 'TaskID', 'TaskSize', 'CyclesPerBit', 
              'TransBitRate', 'DDL', 'SrcName']  # field names
    lambdas = [0.1] * len(ingress_line)  # Average rate of arrivals per time unit for each ingress node
    param_TaskSize = (10, 100 + 1)
    param_CyclesPerBit = (1, 10 + 1)
    param_TransBitRate = (20, 80 + 1)
    param_DDL = (50, 100 + 1)

    # 3. synthetic tasks
    tasks = []
    for node_id, lambda_ in zip(ingress_line, lambdas):
        # Generate inter-arrival times
        inter_arrival_times = np.random.exponential(1 / lambda_, num_arrivals_per_ingress)
        # Compute arrival times
        arrival_times = np.cumsum(inter_arrival_times)
        arrival_times = np.round(arrival_times).tolist()

        for t in arrival_times:
            tasks.append(
                [
                    't0', # TaskName (invalid)
                    t, # GenerationTime
                    0,  # TaskID (invalid)
                    np.random.randint(*param_TaskSize),  # TaskSize
                    np.random.randint(*param_CyclesPerBit),  # CyclesPerBit
                    np.random.randint(*param_TransBitRate),  # TransBitRate
                    np.random.randint(*param_DDL),  # DDL
                    f'n{node_id}',  # SrcName
                ]
            )
    ordered_tasks = sorted(tasks, key=lambda x: x[1])
    for i, item in enumerate(ordered_tasks):
        item[0] = f't{i}'  # TaskName (valid)
        item[2] = i  # TaskID (valid)

    # 4. saving
    if not os.path.exists(save_as):
        data = pd.DataFrame(ordered_tasks, columns=header)
        data.to_csv(save_as, index=False)
    else:
        print(f"File {save_as} already exists!")

    params = {
        'num_arrivals_per_ingress': num_arrivals_per_ingress,
        'lambdas': lambdas,
        'param_TaskSize': param_TaskSize,
        'param_CyclesPerBit': param_CyclesPerBit,
        'param_TransBitRate': param_TransBitRate,
        'param_DDL': param_DDL,
    }
    json_object = json.dumps(params, indent=4)
    if not os.path.exists(params_save_as):
        with open(params_save_as, 'w+') as fw:
            fw.write(json_object)
    else:
        print(f"File {params_save_as} already exists!")

    # 5. loading
    data = pd.read_csv(save_as)
    ordered_tasks = list(data.iloc[:].values)


if __name__ == '__main__':
    main()
