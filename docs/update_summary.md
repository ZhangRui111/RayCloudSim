- **2025/02/04**
  - [**New**] Adding support for the [Pakistan](https://github.com/ZhangRui111/RayCloudSim/blob/main/eval/benchmarks/Pakistan/__init__.py) dataset
  - [**Optimization**] Chosing the refresh rate + the log decimal format
  - [**New**] Calculating the distance from hervetienne coordinate + adding the base latency due to the distance
  - [**New**] Adding Round Robin, Greedy and DQRL Policy

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