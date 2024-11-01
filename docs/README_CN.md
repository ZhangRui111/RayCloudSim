<div style="text-align: center;">
  <img src="https://github.com/ZhangRui111/RayCloudSim/blob/main/docs/imgs/logo_long.jpg" alt="" width="800"/>
</div>

# RayCloudSim: 一款用 Python 编写的用于云/雾/边缘计算的仿真平台

## 更新摘要
- **2024/07/02**
  - [**新增**] 支持数据集 [Topo4MEC](https://github.com/ZhangRui111/RayCloudSim/blob/main/eval/benchmarks/Topo4MEC/__init__.py)

- **2024/04/26**

  - [**新增**] 用户现在可以使用 **json 格式**的配置文件轻松创建 Scenario
  - [**优化**] 数据集优化为使用 **csv 格式**保存，具备更好的可读性
  - [**新增/优化**] 更多、更好的**可视化工具**（包括视频复现的仿真过程），便于对仿真过程的直观认识

- **2024/04/14**

  在分支 main 发布第一个正式版 v1.0.0，主要更新如下：

  - [**新增**] 移除计算单元 (Computational Unit, CU)；采用基于“**CPU频率、CPU周期数**”的计算资源建模方式
  - [**新增**] 仿真过程支持**计算能耗**的建模
  - [**新增**] 计算任务支持**等待超时**的特性
  - [**优化**] **任务队列**优化
  - [**优化**] **README** 文档更新
  - [**优化**] **examples/*** 示例程序更新
  - [**修复**] 修复部分 bug
    - 文件路径导致的模块导入失败
  
> **老用户须知：**
  v1.0.0 之前的版本在分支 pre-v0.6.6 得到了完整保留，但预计后续不再有更新，十分感谢各位用户对于早期版本的支持！

<div style="text-align: center;">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=ZhangRui111/RayCloudSim&type=Date&theme=dark" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=ZhangRui111/RayCloudSim&type=Date" />
    <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=star-history/star-history&type=Date" width="700" />
  </picture>
</div>

## I. 介绍

RayCloudSim 是一个用 Python 编写的轻量级模拟平台，可用于云/雾/边缘计算基础设施和服务的分析建模和仿真。RayCloudSim 的开发初衷是用于任务卸载的相关研究，目前可支持更加多样化的研究课题。

RayCloudSim 有以下优势:
- 源码简洁、轻量化，易于阅读、理解和根据个人需求进行自定义。
- RayCloudSim 是一个基于进程和离散事件的模拟仿真平台，可以尽可能的缩短以现实世界时间衡量的模拟耗时。
- RayCloudSim 可以方便地对接主流的机器学习框架（如 PyTorch、TensorFlow 和其他基于 Python 的机器学习框架）。

RayCloudSim 可以用于以下研究课题:
- 云/雾/边缘计算任务卸载的相关研究
- 云/雾/边缘计算的性能和成本分析
- 复杂网络的流量分析
- 大规模分布式系统的资源管理和调度策略研究
- 特定设备的部署策略研究，如联邦学习中的参数服务器
- ...

## II. 安装和相关依赖

主要依赖模块：

- **python >= 3.8**：更早的 Python 版本可能可行，但是没有经过测试
- **networkx**：NetworkX 是一个用于创建、操作和研究复杂网络的结构、动态和功能的 Python 包
- **simpy**：SimPy 是一个基于标准 Python 的基于进程的离散事件仿真框架
- **numpy**：NumPy 是一个用于数组操作的 Python 库
- **pandas**：Pandas 是一个快速、强大、灵活且易于使用的开源数据分析和处理工具

以下模块用于可视化工具：

- **matplotlib**
- **cv2**
- **tensorboard**

推荐使用 Anaconda 配置 RayCloudSim 运行环境的相关命令：

```text
conda create --name raycloudsim python=3.8
conda activate raycloudsim
pip install -r requirements.txt
```

## III. 起航
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

**3.2.1** 下图展示了 RayCloudSim 的框架架构，主要包含两大部分：`Env` 和 `Task`：

[comment]: <> (![RayCloudSim 的框架架构]&#40;docs/framework.jpg&#41;)

<div style="text-align: center;">
  <img src="https://github.com/ZhangRui111/RayCloudSim/blob/main/docs/imgs/raycloudsim.png" alt="RayCloudSim 的框架架构" width="600"/>
</div>

**3.2.2** 一个简单的系统建模介绍：[docs/RayCloudSim.md](docs/RayCloudSim.md)

**3.2.3** 以下示例程序可以看做是渐进式的使用教程。

- [examples/demo1.py](https://github.com/ZhangRui111/RayCloudSim/blob/main/examples/demo1.py)

- [examples/demo2.py](https://github.com/ZhangRui111/RayCloudSim/blob/main/examples/demo2.py)

- [examples/demo3.py](https://github.com/ZhangRui111/RayCloudSim/blob/main/examples/demo3.py)

- [examples/demo4.py](https://github.com/ZhangRui111/RayCloudSim/blob/main/examples/demo4.py)

- [examples/demo5.py](https://github.com/ZhangRui111/RayCloudSim/blob/main/examples/demo5.py)

- [examples/demo6.py](https://github.com/ZhangRui111/RayCloudSim/blob/main/examples/demo6.py)

- [examples/demo7.py](https://github.com/ZhangRui111/RayCloudSim/blob/main/examples/demo7.py)

- [examples/demo8.py](https://github.com/ZhangRui111/RayCloudSim/blob/main/examples/demo8.py)

需要注意的是学会使用 [Simpy](https://simpy.readthedocs.io/en/latest/contents.html) 对于使用 RayCloudSim 会很有帮助.

**3.2.4** RayCloudSim 支持多个可视化功能：系统拓扑静态可视化、仿真过程动态可视化等

- 系统拓扑静态可视化

<div style="text-align: center;">
  <img src="https://github.com/ZhangRui111/RayCloudSim/blob/main/examples/vis/demo_base.png" alt="" width="400"/>
</div>

- 仿真过程动态可视化

<div style="text-align: center;">
  <img src="https://github.com/ZhangRui111/RayCloudSim/blob/main/docs/gifs/simulation_vis1.gif" alt="" width="600"/>
</div>

<div style="text-align: center;">
  <img src="https://github.com/ZhangRui111/RayCloudSim/blob/main/docs/gifs/simulation_vis2.gif" alt="" width="600"/>
</div>

完整视频:

 - [Github](https://github.com/ZhangRui111/RayCloudSim/blob/main/docs/videos/out.avi)

 - [百度网盘 (提取码: xa1r)](https://pan.baidu.com/s/16X1Mdn-wvMu_o4GpUFtRDw?pwd=xa1r)

## IV. 开发计划
### 1. 未来更新计划

> 后续更新请参照[更新摘要](https://github.com/ZhangRui111/RayCloudSim/blob/main/docs/README_CN.md#%E6%9B%B4%E6%96%B0%E6%91%98%E8%A6%81)

- [x] 基本版本。(2023/05/10)
- [X] 增加模块 zoo, 如 WirelessNode 等。(2023/10/24)
- [X] 计算节点支持队列空间, 以支持任务缓存。(2023/11/10)
<!-- - [ ] ~~支持把无线节点作为中继通信节点?~~ -->
- [X] 支持对于“计算能耗”、“任务超时”的建模等。(2024/04/14)
<!-- - [ ] Modeling of divisible tasks (Application >>> Task) -->
<!-- - [ ] Details such as the energy consumption and transmission of wireless nodes -->
- [X] Metric/* (2024/04/16)
- [X] Evaluation APIs (2024/04/16)
- [ ] Anything reasonable

### 2. 向 RayCloudSim 贡献代码
欢迎任何对代码库的贡献。但是请注意, 分支**main**是受保护的，建议您提交/推送代码到分支**dev-open**。

<img src="https://github.com/ZhangRui111/RayCloudSim/blob/main/docs/imgs/timG.jpg" alt="RayCloudSim 交流QQ群" width="250"/>

欢迎加入RayCloudSim 交流QQ群，推荐入群后备注研究方向

<!-- ## Citation

引用本代码项目 RayCloudSim 时，您可以使用以下 BibTeX 条目：

```text
@article{zhang2022osttd,
  title={OSTTD: Offloading of Splittable Tasks with Topological Dependence in Multi-Tier Computing Networks},
  author={Zhang, Rui and Chu, Xuesen and Ma, Ruhui and Zhang, Meng and Lin, Liwei and Gao, Honghao and Guan, Haibing},
  journal={IEEE Journal on Selected Areas in Communications},
  year={2022},
  publisher={IEEE}
}
```

此外, RayCloudSim 的开发受到了 [LEAF](https://github.com/dos-group/leaf) 的启发，因此，也建议引用以下文献。

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
