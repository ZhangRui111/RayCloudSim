<div style="text-align: center;">
  <img src="https://github.com/ZhangRui111/RayCloudSim/blob/main/docs/imgs/logo_long.jpg" alt="" width="800"/>
</div>

# RayCloudSim: A Simulation Platform Written in Python for Cloud/Fog/Edge Computing

[<img src="https://img.shields.io/badge/License-MIT-blue.svg" height="20px" />](https://github.com/ZhangRui111/RayCloudSim/blob/main/LICENSE)

> [!IMPORTANT]
> 
> **For researchers starting a new project, we recommend using our newer simulator:**
> 
> 👉 **[UbiCompSim](https://github.com/NexusMindLab/UbiCompSim)**
> 
> UbiCompSim is designed as a **unified simulation platform for ubiquitous computing**, built with **Python + SimPy + NetworkX**. Compared with RayCloudSim, it provides a more modern and extensible architecture for studying not only task offloading, but also broader ubiquitous computing scenarios.
> 
> ### 📢 Why move to UbiCompSim?
> 
> UbiCompSim extends the scope of simulation from traditional Cloud/Fog/Edge settings to more general **ubiquitous computing environments**, with support for:
> 
> - **Layered and plugin-oriented architecture**, making it easier to customize and extend
> - **Dynamic topology management**, including link creation and disconnection caused by node mobility
> - **Heterogeneous node types**, such as cloud centers, edge servers, RSUs, UAVs, and mobile terminals
> - **Mobility modeling**, including RandomWaypoint and future mobility extensions
> - **Fine-grained monitoring and visualization**, with CSV export and automatic chart generation
> - **Flexible offloading strategies**, with clearer abstractions for experimentation
> - **Progressive tutorials**, helping new users get started quickly
> 
> RayCloudSim will continue to receive limited maintenance updates, while major new features will primarily be introduced in **[UbiCompSim](https://github.com/NexusMindLab/UbiCompSim)**.

## I. Update Summary

> Only the summaries of the **most recent three updates** will be recorded here. The complete history of all update summaries can be viewed [here](https://github.com/ZhangRui111/RayCloudSim/blob/main/docs/update_summary.md).

- **2025/09/01**
  - [**New**] RayCloudSim now supports dynamic node online/offline operations during simulation. For more details on this functionality, please refer to [demo7.py](https://github.com/ZhangRui111/RayCloudSim/blob/main/examples/demo7.py) or [demo7.ipynb](https://github.com/ZhangRui111/RayCloudSim/blob/main/examples/demo7.ipynb).
  - [**New**] RayCloudSim now utilizes unified task [status codes](https://github.com/ZhangRui111/RayCloudSim/blob/main/core/code.py), providing clearer indications of each task's execution state.
  - [**Optimization**] The functionality of *EnvLogger* has been refined.
  - [**Fix**] The following bugs have been fixed:
    - An issue with TimeoutError counting.
    - An error in task process management (specifically, the failure to correctly close faulty task processes).
    - Please note that duplicate task IDs are no longer treated as errors.

- **2025/05/07**
  - [**Optimization**] Main branch: Retains only the most necessary and core code and functionality, with the highest readability and the smallest codebase.

- **2025/02/04**
  - [**New**] New dataset: [Pakistan](https://github.com/ZhangRui111/RayCloudSim/blob/main/eval/benchmarks/Pakistan/__init__.py)
  - [**New**] Adding support for distance calculation based on the Haversine formula
  - [**New**] New offloading policies: Round Robin, Greedy and DQRL

## II. Contributing

Any contributions you make are greatly appreciated. Please make sure to read the [Code of Contribution](https://github.com/ZhangRui111/RayCloudSim/blob/main/docs/code_of_contribution.md) before submitting a PR.

### Join and build RayCloudSim together

<a href="https://github.com/tutur90">
  <img src="https://avatars.githubusercontent.com/u/124059682?v=4" alt="tutur90" width="60" />
</a>

<div style="text-align: center;">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=ZhangRui111/RayCloudSim&type=Date&theme=dark" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=ZhangRui111/RayCloudSim&type=Date" />
    <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=star-history/star-history&type=Date" width="500" />
  </picture>
</div>

## III. Introduction

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

**The project has three branches:**

- **main**:
    - Retains only the most necessary and core code and functionality, with the highest readability and the smallest codebase.
    - **PR policy**: Almost no PRs will be accepted, except for those that fix bugs.

- **dev-open**:
    - Based on the main branch, it is open to any functional additions and code optimizations.
    - **PR policy**: Open to any PRs, but the code that overlaps with the main branch must remain consistent.

- **pre-v0.6.6**:
    - An early version of the project, used only for backup and has been abandoned.
    - **PR policy**: No PRs will be accepted.

## IV. Requirements & Installation

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

## V. Set Sail
### 1. Hello World

```python
# Create the environment with the specified scenario and configuration files.
scenario = Scenario(config_file="examples/scenarios/configs/config_1.json")
env = Env(scenario, config_file="core/configs/env_config_null.json")

# Begin the simulation with a specified task.
task = Task(
    id=0,
    task_size=20,
    cycles_per_bit=10,
    trans_bit_rate=20,
    src_name='n0',
)

# Process the task and specify the destination node.
env.process(task=task, dst_name='n1')

# Run the simulation for 20 time units.
env.run(until=20)

# Close the environment after simulation.
env.close()
```

Simulation log:

```text
[0.00]: Task {0} generated in Node {n0}
[0.00]: Task {0}: {n0} --> {n1}
[1.00]: Task {0} arrived Node {n1} with {1.00}s
[1.00]: Processing Task {0} in {n1}
[11.00]: Task {0}: Completed in Node {n1} with execution time {10.00}s
[20.00]: Simulation completed!
```

### 2. Tutorials

**(1).** The following figure presents the framework of RayCloudSim, which consists of two main components：`Env` and `Task`: 

[comment]: <> (![The framework of RayCloudSim]&#40;docs/framework.jpg&#41;)

<div style="text-align: center;">
  <img src="https://github.com/ZhangRui111/RayCloudSim/blob/main/docs/imgs/raycloudsim.png" alt="The framework of RayCloudSim" width="600"/>
</div>

**(2).** A Simple Introduction to System Modeling: [docs/RayCloudSim.md](docs/RayCloudSim.md)

**(3).** The following scripts can be used as progressive tutorials.

- [examples/*](https://github.com/ZhangRui111/RayCloudSim/blob/main/examples)

Note that learning how to use [Simpy](https://simpy.readthedocs.io/en/latest/contents.html) would be very helpful.

**(4).** RayCloudSim supports multiple visualization features: static visualization of system topology, dynamic visualization of the simulation process, etc.

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

## VI. Citation

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
