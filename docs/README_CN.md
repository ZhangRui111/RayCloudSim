# RayCloudSim: 一款用 Python 编写的用于云/雾/边缘计算的模拟平台

## I. 介绍

RayCloudSim 是使用 Python 开发编写的模拟平台，可用于云计算、雾计算或边缘计算环境下的分析建模。

RayCloudSim 有以下优势:
- 源码简洁、轻量化，易于阅读、理解和根据个人需求进行自定义。
- RayCloudSim 是一个基于进程和离散事件的模拟仿真平台，可以尽可能的缩短以现实世界时间衡量的模拟耗时。
- RayCloudSim 可以方便地对接主流的机器学习框架（如 PyTorch、TensorFlow 和其他基于 Python 的机器学习框架）。

RayCloudSim 可以用于以下研究课题:
- 云计算和边缘计算的性能和成本分析
- 复杂网络的流量分析
- 大规模分布式系统的资源管理和调度策略研究
- 计算任务的分配和调度算法研究
- 特定设备的部署策略研究，如联邦学习中的参数服务器
- ...

## II. 安装和相关依赖

- **python >= 3.8** 
  
    更早的 Python 版本可能可行，但是没有经过测试。
- **numpy**
- **networkx**
- **simpy**

以下包用于可视化，是可选的。

- **matplotlib**
- **plotly**
- **kaleido**

```
conda create --name raycloudsim python=3.8
conda activate raycloudsim
conda install -c anaconda numpy
conda install -c conda-forge matplotlib
conda install -c anaconda networkx
conda install -c conda-forge simpy
conda install -c plotly plotly
conda install -c conda-forge python-kaleido
```

## III. 起航
### 1. Hello World

```
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

模拟打印信息:

```
[0.00]: Task {0} generated in Node {n0}
[4.00]: Task {0} arrived Node {n1} with {4.00}s
[6.00]: Task {0} accomplished in Node {n1} with {2.00}s
[10.00]: Simulation completed!
```

### 2. 指导

![RayCloudSim 的框架架构](docs/framework.jpg)

<img src="https://github.com/ZhangRui111/RayCloudSim/blob/main/docs/framework.jpg" alt="RayCloudSim 的框架架构" width="800"/>

- 需要注意的是学会使用 [Simpy](https://simpy.readthedocs.io/en/latest/contents.html) 对于使用 RayCloudSim 会很有帮助.

- [docs/RayCloudSim.md](docs/RayCloudSim.md)

### 3. Tutorials

以下示例程序可以看做是渐进式的使用教程。

- `examples/demo1.py`

- `examples/demo2.py`

- `examples/demo3.py`

- `examples/demo4.py`

## IV. 未来更新计划
- [x] 基本版本 (2023/05/10)。
- [ ] 支持在资源（如带宽、计算资源/CU）不足时，任务可以等待一段时间。
- [ ] 支持对于“能源消耗”的建模。
- [ ] 打包并发布到 PyPI.

## Citation

引用本代码项目 RayCloudSim 时，您可以使用以下 BibTeX 条目：

```
@article{zhang2022osttd,
  title={OSTTD: Offloading of Splittable Tasks with Topological Dependence in Multi-Tier Computing Networks},
  author={Zhang, Rui and Chu, Xuesen and Ma, Ruhui and Zhang, Meng and Lin, Liwei and Gao, Honghao and Guan, Haibing},
  journal={IEEE Journal on Selected Areas in Communications},
  year={2022},
  publisher={IEEE}
}
```

此外, RayCloudSim 的开发受到了 [LEAF](https://github.com/dos-group/leaf) 的启发，因此，也建议引用以下文献。

```
@inproceedings{WiesnerThamsen_LEAF_2021,
  author={Wiesner, Philipp and Thamsen, Lauritz},
  booktitle={2021 IEEE 5th International Conference on Fog and Edge Computing (ICFEC)}, 
  title={{LEAF}: Simulating Large Energy-Aware Fog Computing Environments}, 
  year={2021},
  pages={29-36},
  doi={10.1109/ICFEC51620.2021.00012}
}
```
