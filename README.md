<div style="text-align: center;">
  <img src="https://github.com/ZhangRui111/RayCloudSim/blob/main/docs/imgs/logo_long.jpg" alt="" width="800"/>
</div>

# RayCloudSim: A Simulator Written in Python for Cloud, Fog, or Edge Computing

<div style="text-align: center;">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=ZhangRui111/RayCloudSim&type=Date&theme=dark" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=ZhangRui111/RayCloudSim&type=Date" />
    <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=star-history/star-history&type=Date" width="700" />
  </picture>
</div>

## Update Summary
- **2024/04/14**

  The first official release v1.0.0 has been published on the main branch, with the following major updates:

  - [**New**] Removal of the "Computational Unit" (CU); adoption of a computational resource modeling approach based on "**CPU frequency, number of CPU cycles**"
  - [**New**] Simulation process now supports modeling of **computational energy consumption**
  - [**New**] Computational tasks now support the feature of **timeout failure**
  - [**Optimization**] Optimization of the **task queue**
  - [**Optimization**] **README** documentation updated
  - [**Optimization**] **examples/*** Example programs updated
  - [**Fix**] Fixed some bugs
    - Module import failures caused by file paths

> **Important Notice for Previous Users:**
The versions prior to v1.0.0 have been preserved on the pre-v0.6.6 branch, but no further updates are expected for this version. We are very grateful for the support of all users for the early versions!

## I. Introduction

RayCloudSim is a lightweight simulator written in Python for analytical modeling and simulation of Cloud/Fog/Edge Computing infrastructures and services.

RayCloudSim has the following advantages: 
- Compact source code, which is easy to read, understand and customize according to individual needs.
- It is a process-based discrete-event simulation framework and can be performed "as fast as possible", in wall clock time.
- It is easy to integrate with machine learning frameworks such as PyTorch, TensorFlow, and other Python-based ML frameworks.

RayCloudSim can be used for the following research topics:
- Performance and cost analysis of cloud computing and edge computing
- Traffic analysis of complex networks
- Research on resource management and scheduling strategies for large-scale distributed systems
- Research on task allocation and scheduling algorithms
- Research on deployment of specific devices, such as parameter servers in federated learning.
- ...

## II. Requirements & Installation

- **python >= 3.8** 
  
    previous version might be OK but without testing.
- **numpy**
- **networkx**
- **simpy**
  
The following packages are optional for visualization.

- **matplotlib**
- **plotly**
- **kaleido**

Commands for configuring the RayCloudSim using Anaconda:

```text
conda create --name raycloudsim python=3.8
conda activate raycloudsim
conda install -c anaconda numpy
conda install -c conda-forge matplotlib
conda install -c anaconda networkx
conda install -c conda-forge simpy
conda install -c plotly plotly
conda install -c conda-forge python-kaleido
```

## III. Set Sail
### 1. Hello World

```python
# Create the Env
env = Env(scenario=Scenario())

# Begin Simulation
task = Task(task_id=0,
            task_size=20,
            cycles_per_bit=10,
            trans_bit_rate=20,
            src_name='n0')

env.process(task=task, dst_name='n1')

env.run(until=20)

print("\n-----------------------------------------------")
print("Power consumption during simulation:\n")
print(f"n0: {env.scenario.get_node('n0').power_consumption:.3f}")
print(f"n1: {env.scenario.get_node('n1').power_consumption:.3f}")
print("-----------------------------------------------\n")

env.close()
```

Simulation log:

```text
[0.00]: Task {0} generated in Node {n0}
[0.00]: Task {0}: {n0} --> {n1}
[1.00]: Task {0} arrived Node {n1} with {1.00}s
[1.00]: Processing Task {0} in {n1}
[11.00]: Task {0} accomplished in Node {n1} with {10.00}s

-----------------------------------------------
Power consumption during simulation:

n0: 0.200
n1: 72000.200
-----------------------------------------------

[20.00]: Simulation completed!
```

### 2. Guides

- The following figure presents the framework of RayCloudSim, which consists of two main components：`Env` and `Task`: 

[comment]: <> (![The framework of RayCloudSim]&#40;docs/framework.jpg&#41;)

<div style="text-align: center;">
  <img src="https://github.com/ZhangRui111/RayCloudSim/blob/main/docs/imgs/framework.jpg" alt="RayCloudSim 的框架架构" width="500"/>
</div>

- Note that learning how to use [Simpy](https://simpy.readthedocs.io/en/latest/contents.html) would be very helpful.

- A Simple Introduction to System Modeling: [docs/RayCloudSim.md](docs/RayCloudSim.md)

### 3. Tutorials

The following scripts can be used as progressive tutorials.

- [examples/demo1.py](https://github.com/ZhangRui111/RayCloudSim/blob/main/examples/demo1.py)

- [examples/demo2.py](https://github.com/ZhangRui111/RayCloudSim/blob/main/examples/demo2.py)

- [examples/demo3.py](https://github.com/ZhangRui111/RayCloudSim/blob/main/examples/demo3.py)

- [examples/demo4.py](https://github.com/ZhangRui111/RayCloudSim/blob/main/examples/demo4.py)

- [examples/demo5.py](https://github.com/ZhangRui111/RayCloudSim/blob/main/examples/demo5.py)

- [examples/demo6.py](https://github.com/ZhangRui111/RayCloudSim/blob/main/examples/demo6.py)

The following figure illustrates a visualization example:

<div style="text-align: center;">
  <img src="https://github.com/ZhangRui111/RayCloudSim/blob/main/examples/vis/network_demo3.png" alt="可视化示例" width="500"/>
</div>

## IV. Development Plan
### 1. TODO
- [X] The basic version. (2023/05/10)
- [X] Added modules zoo, including WirelessNode, etc. (2023/10/24)
- [X] Computational nodes now support queue space to facilitate task buffering. (2023/11/10)
- [ ] ~~Support using wireless nodes as relay communication nodes?~~
- [X] Modeling of 'computational energy consumption' and 'task timeout' supported, etc. (2024/04/14)
- [ ] Modeling of divisible tasks
- [ ] Details such as the energy consumption and transmission of wireless nodes
- [X] Metric/* (2024/04/16)
- [X] Evaluation APIs (2024/04/16)
- [ ] Anything reasonable

### 2. Contribute Code to RayCloudSim
We welcome any contributions to the codebase. However, please note that the **main** branch is protected, and we recommend that you submit/push your code to the **dev-open** branch.

## Citation

To cite this repository, you can use the following BibTeX entry:

```text
@article{zhang2022osttd,
  title={OSTTD: Offloading of Splittable Tasks with Topological Dependence in Multi-Tier Computing Networks},
  author={Zhang, Rui and Chu, Xuesen and Ma, Ruhui and Zhang, Meng and Lin, Liwei and Gao, Honghao and Guan, Haibing},
  journal={IEEE Journal on Selected Areas in Communications},
  year={2022},
  publisher={IEEE}
}
```

Besides, RayCloudSim is inspired by [LEAF](https://github.com/dos-group/leaf) and the following citation is also recommended.

```text
@inproceedings{WiesnerThamsen_LEAF_2021,
  author={Wiesner, Philipp and Thamsen, Lauritz},
  booktitle={2021 IEEE 5th International Conference on Fog and Edge Computing (ICFEC)}, 
  title={{LEAF}: Simulating Large Energy-Aware Fog Computing Environments}, 
  year={2021},
  pages={29-36},
  doi={10.1109/ICFEC51620.2021.00012}
}
```

## More

- [中文文档](docs/README_CN.md)
