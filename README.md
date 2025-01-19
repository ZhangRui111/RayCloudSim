<div style="text-align: center;">
  <img src="https://github.com/ZhangRui111/RayCloudSim/blob/main/docs/imgs/logo_long.jpg" alt="" width="800"/>
</div>

# RayCloudSim: A Simulation Platform Written in Python for Cloud/Fog/Edge Computing

[<img src="https://img.shields.io/badge/License-MIT-blue.svg" height="30px" />](https://github.com/ZhangRui111/RayCloudSim/blob/main/LICENSE) [<img src="https://api.gitsponsors.com/api/badge/img?id=638982897" height="30">](https://api.gitsponsors.com/api/badge/link?p=JIrAC5FDNZDuOserq1+rtK+ePrdHC6pqFQMndZ+SGnLnSZE6kl4J4Dp3L4yJ1EunkradtRRZ0Nn4KY4O6aHr0kZk/a7DLTdz6bFIn667HJuIoij3RANSfBXi+eoJVy1zDTde6CE8enSRQddgwpgVPQ==)

## Update Summary
- **2024/07/02**
  - [**New**] Adding support for the [Topo4MEC](https://github.com/ZhangRui111/RayCloudSim/blob/main/eval/benchmarks/Topo4MEC/__init__.py) dataset

- **2024/04/26**

  - [**New**] Users can now easily create the Scenario using configuration files in **JSON** format
  - [**Optimization**] The dataset has been optimized for saving in **CSV** format, offering better readability
  - [**New/Optimization**] More and better **visualization tools**, including simulation processes reproduced in video format, facilitate an intuitive understanding of the simulation process

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

<div style="text-align: center;">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=ZhangRui111/RayCloudSim&type=Date&theme=dark" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=ZhangRui111/RayCloudSim&type=Date" />
    <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=star-history/star-history&type=Date" width="700" />
  </picture>
</div>

## I. Introduction

RayCloudSim is a lightweight simulator written in Python for analytical modeling and simulation of Cloud/Fog/Edge Computing infrastructures and services. The original intention for the development of RayCloudSim was for research related to task offloading, and it now supports a more diverse range of research topics.

RayCloudSim has the following advantages: 
- Compact source code, which is easy to read, understand and customize according to individual needs.
- It is a process-based discrete-event simulation framework and can be performed "as fast as possible", in wall clock time.
- It is easy to integrate with machine learning frameworks such as PyTorch, TensorFlow, and other Python-based ML frameworks.

RayCloudSim can be used for the following research topics:
- Research on task offloading in cloud/fog/edge computing
- Research on performance and cost analysis of cloud/fog/edge computing
- Research on traffic analysis of complex networks
- Research on resource management and scheduling strategies for large-scale distributed systems
- Research on deployment strategies for specific devices, such as parameter servers in federated learning
- ...

## II. Requirements & Installation

Main Dependent Modules:

- **python >= 3.8**: Previous versions might be OK but without testing.
- **networkx**: NetworkX is a Python package for the creation, manipulation, and study of the structure, dynamics, and functions of complex networks.
- **simpy**: SimPy is a process-based discrete-event simulation framework based on standard Python.
- **numpy**: NumPy is a Python library used for working with arrays.
- **pandas**: Pandas is a fast, powerful, flexible and easy to use open source data analysis and manipulation tool.
  
The following modules are used for visualization tools:

- **matplotlib**
- **cv2**
- **tensorboard**

Users are recommended to use the Anaconda to configure the RayCloudSim:

```text
conda create --name raycloudsim python=3.8
conda activate raycloudsim
pip install -r requirements.txt
```

## III. Set Sail
### 3.1 Hello World

```python
# Create the Env
scenario=Scenario(config_file="examples/scenarios/configs/config_1.json")
env = Env(scenario, config_file="core/configs/env_config.json")

# Begin Simulation
task = Task(task_id=0,
            task_size=20,
            cycles_per_bit=10,
            trans_bit_rate=20,
            src_name='n0')

env.process(task=task, dst_name='n1')

env.run(until=20)

print("\n-----------------------------------------------")
print("Energy consumption during simulation:\n")
print(f"n0: {env.node_energy('n0'):.3f}")
print(f"n1: {env.node_energy('n1'):.3f}")
print(f"Averaged: {env.avg_node_energy():.3f}")
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
Energy consumption during simulation:

n0: 0.000
n1: 0.072
Averaged: 0.036
-----------------------------------------------

[20.00]: Simulation completed!
```

### 3.2 Tutorials

**3.2.1** The following figure presents the framework of RayCloudSim, which consists of two main components：`Env` and `Task`: 

[comment]: <> (![The framework of RayCloudSim]&#40;docs/framework.jpg&#41;)

<div style="text-align: center;">
  <img src="https://github.com/ZhangRui111/RayCloudSim/blob/main/docs/imgs/raycloudsim.png" alt="The framework of RayCloudSim" width="600"/>
</div>

**3.2.2** A Simple Introduction to System Modeling: [docs/RayCloudSim.md](docs/RayCloudSim.md)

**3.2.3** The following scripts can be used as progressive tutorials.

- [examples/demo1.py](https://github.com/ZhangRui111/RayCloudSim/blob/main/examples/demo1.py)

- [examples/demo2.py](https://github.com/ZhangRui111/RayCloudSim/blob/main/examples/demo2.py)

- [examples/demo3.py](https://github.com/ZhangRui111/RayCloudSim/blob/main/examples/demo3.py)

- [examples/demo4.py](https://github.com/ZhangRui111/RayCloudSim/blob/main/examples/demo4.py)

- [examples/demo5.py](https://github.com/ZhangRui111/RayCloudSim/blob/main/examples/demo5.py)

- [examples/demo6.py](https://github.com/ZhangRui111/RayCloudSim/blob/main/examples/demo6.py)

- [examples/demo7.py](https://github.com/ZhangRui111/RayCloudSim/blob/main/examples/demo7.py)

- [examples/demo8.py](https://github.com/ZhangRui111/RayCloudSim/blob/main/examples/demo8.py)

Note that learning how to use [Simpy](https://simpy.readthedocs.io/en/latest/contents.html) would be very helpful.

**3.2.4** RayCloudSim supports multiple visualization features: static visualization of system topology, dynamic visualization of the simulation process, etc.

- static visualization of system topology

<div style="text-align: center;">
  <img src="https://github.com/ZhangRui111/RayCloudSim/blob/main/examples/vis/demo_base.png" alt="" width="400"/>
</div>

- dynamic visualization of the simulation process

<div style="text-align: center;">
  <img src="https://github.com/ZhangRui111/RayCloudSim/blob/main/docs/gifs/simulation_vis1.gif" alt="" width="600"/>
</div>

<div style="text-align: center;">
  <img src="https://github.com/ZhangRui111/RayCloudSim/blob/main/docs/gifs/simulation_vis2.gif" alt="" width="600"/>
</div>

The complete video:

 - [Github](https://github.com/ZhangRui111/RayCloudSim/blob/main/docs/videos/out.avi)

 - [Baidu Netdisk (Access code: xa1r)](https://pan.baidu.com/s/16X1Mdn-wvMu_o4GpUFtRDw?pwd=xa1r)

## IV. Development Plan
### 4.1 TODO

> For subsequent updates, please refer to the [update summary](https://github.com/ZhangRui111/RayCloudSim/blob/main/README.md#update-summary)

- [X] The basic version. (2023/05/10)
- [X] Added modules zoo, including WirelessNode, etc. (2023/10/24)
- [X] Computational nodes now support queue space to facilitate task buffering. (2023/11/10)
<!-- - [ ] ~~Support using wireless nodes as relay communication nodes?~~ -->
- [X] Modeling of 'computational energy consumption' and 'task timeout' supported, etc. (2024/04/14)
<!-- - [ ] Modeling of divisible tasks (Application >>> Task)-->
<!-- - [ ] Details such as the energy consumption and transmission of wireless nodes -->
- [X] Metric/* (2024/04/16)
- [X] Evaluation APIs (2024/04/16)
- [ ] Anything reasonable

### 4.2 Contribute Code to RayCloudSim
We welcome any contributions to the codebase. However, please note that the **main** branch is protected, and we recommend that you submit/push your code to the **dev-open** branch.

<!-- ## Citation

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
``` -->

## More

- [中文文档](docs/README_CN.md)
