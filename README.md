<img src="https://github.com/ZhangRui111/RayCloudSim/blob/main/docs/imgs/logo_long.jpg" alt="" width="800"/>

# RayCloudSim: A Simulator Written in Python for Cloud, Fog, or Edge Computing

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=ZhangRui111/RayCloudSim&type=Date&theme=dark" />
  <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=ZhangRui111/RayCloudSim&type=Date" />
  <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=star-history/star-history&type=Date" />
</picture>

## I. Introduction

RayCloudSim is a simulator written in Python for analytical modeling in cloud, fog, or edge computing environments. 

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
            max_cu=10,
            task_size_exe=20,
            task_size_trans=10,
            bit_rate=20,
            src_name='n0')

env.process(task=task, dst_name='n1')

env.run(until=10)

env.close()
```

Simulation log:

```text
[0.00]: Task {0} generated in Node {n0}
[4.00]: Task {0} arrived Node {n1} with {4.00}s
[6.00]: Task {0} accomplished in Node {n1} with {2.00}s
[10.00]: Simulation completed!
```

### 2. Guides

- The following figure presents the framework of RayCloudSim, which consists of two main components：`Env` and `Task`: 

[comment]: <> (![The framework of RayCloudSim]&#40;docs/framework.jpg&#41;)

<img src="https://github.com/ZhangRui111/RayCloudSim/blob/main/docs/imgs/framework.jpg" alt="The framework of RayCloudSim" width="600"/>

- Note that learning how to use [Simpy](https://simpy.readthedocs.io/en/latest/contents.html) would be very helpful.

- [docs/RayCloudSim.md](docs/RayCloudSim.md)

### 3. Tutorials

The following scripts can be used as progressive tutorials.

- [examples/demo1.py](https://github.com/ZhangRui111/RayCloudSim/blob/main/examples/demo1.py)

- [examples/demo2.py](https://github.com/ZhangRui111/RayCloudSim/blob/main/examples/demo2.py)

- [examples/demo3.py](https://github.com/ZhangRui111/RayCloudSim/blob/main/examples/demo3.py)

- [examples/demo4.py](https://github.com/ZhangRui111/RayCloudSim/blob/main/examples/demo4.py)

The following figure illustrates a visualization example:

<img src="https://github.com/ZhangRui111/RayCloudSim/blob/main/examples/vis/network_demo3.png" alt="visualization example" width="500"/>

## IV. Development Plan
### 1. TODO
- [X] The basic version. (2023/05/10)
- [X] Module Zoo, such as WirelessNode, etc. (2023/10/24) **\[branch dev\]**
- [ ] Support using wireless nodes as relay communication nodes.
- [ ] Add cache space to computing nodes for task queue.
- [ ] Modeling of energy consumption.
- [ ] Package and publish to PyPI.

### 2. Contribute Code to RayCloudSim
We welcome any contributions to the codebase. The branch **main** is protected, and we recommend that you submit/push code to branch **dev**. 

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
