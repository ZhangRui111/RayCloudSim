import os
import json
import numpy as np
import pandas as pd


def main():
    # 1. loading source files
    flag, num_arrivals_per_ingress, lambda_, ingress_line = '25N50E', 5000, 0.04, list(range(25))
    # flag, num_arrivals_per_ingress, lambda_, ingress_line = '50N50E', 2500, 0.02, list(range(50))
    # flag, num_arrivals_per_ingress, lambda_, ingress_line = '100N150E', 1250, 0.01, list(range(100))
    # flag, num_arrivals_per_ingress, lambda_, ingress_line = 'MilanCityCenter', 5000, 0.03333, list(range(30))

    save_as = f"eval/benchmarks/Topo4MEC/data/{flag}/trainset.csv"
    params_save_as = f"eval/benchmarks/Topo4MEC/data/{flag}/trainset_configs.json"

    # 2. parameters
    header = ['TaskName', 'GenerationTime', 'TaskID', 'TaskSize', 'CyclesPerBit', 
              'TransBitRate', 'DDL', 'SrcName']  # field names
    lambdas = [lambda_] * len(ingress_line)  # Average rate of arrivals per time unit for each ingress node
    param_TaskSize = (10, 100 + 1)  # Mb
    param_CyclesPerBit = (100, 1000 + 1)  # per-MBit
    param_TransBitRate = (1, 5)  # Mbps
    param_DDL = (20, 100 + 1)  # s

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
                    10 * np.random.randint(*param_TransBitRate),  # TransBitRate
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
        'ingress': ingress_line,
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
