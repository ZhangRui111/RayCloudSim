<div style="text-align: center;">
  <img src="https://github.com/ZhangRui111/RayCloudSim/blob/main/docs/imgs/logo_long.jpg" alt="" width="800"/>
</div>

# RayCloudSim

Note: This README file is recommended to be viewed with a reader that supports LaTeX.

## 1. Attribute Modeling

1. **Node**:
    - node_id: node id, unique
    - name: node name.
    - max_cpu_freq: maximum cpu frequency.
    - free_cpu_freq: current available cpu frequency.
    - task_buffer: FIFO buffer for queued tasks.
    - location: geographical location.
    - idle_energy_coef: energy consumption coefficient during idle state.
    - exe_energy_coef: energy consumption coefficient during working state.
    - energy_consumption: energy consumption since the simulation begins.
    - energy budget (for those energy-sensitive devices)

2. **Link**:
    - src: source node.
    - dst: destination node.
    - max_bandwidth: maximum bandwidth in bps.
    - free_bandwidth: current available bandwidth in bps.
    - dis: the distance between its source node and its destination node.
    - base_latency: base latency of the link.
    - data_flows: data flows allocated in this link.

3. **Task**:
    - task_id: task id, unique.
    - task_size: task size in bits.
    - cycles_per_bit: amount of CPU cycles per bit of task data.
    - trans_bit_rate: bit rate of data flow.
    - ddl: maximum tolerable time limit before executing since the task is generated, i.e., wait_time <= ddl.

    - cpu_freq: obtained cpu frequency during real execution.

    - wait_time: waiting time from task generation to execution, including the transmission time and the queuing time in the dst node.
        - trans_time: time being transmitted from the src node to the dst node, which is part of the waiting time.
    - exe_time: time being processed in the dst node.

## 2. Dynamic Modeling

Here, [ ] indicates that the value depends on what it is related to.

### 2.1 Time

1. **Waiting Time**

    $$t^{wait} = \frac{q \cdot c}{f}$$

    - $q$: total size of all queued tasks preceding the current task [Task]
    - $c$: amount of CPU cycles per bit [Task]
    - $f$: CPU frequency [Node]

    - **Note that**, for simplicity, the transmission time term in the expression is omitted. 
    The transmission time is denoted as:

        $$t^{trans} = \frac{d}{B} \cdot n$$

        - $d$: task size in bits [Task]
        - $B$: bandwidth [Link]
        - $n$: multi-hop routing [Link/System]

2. **Execution Time**

    $$t^{exe} = \frac{d \cdot c}{f}$$

### 2.2 Energy Consumption

1. **Idle Energy Consumption**

    $$e^{idle} = \alpha \cdot t^{idle}$$

    - $\alpha$: idle_energy_coef, energy consumption coefficient during idle state [Node]
    - $t^{idle}$: idle time

2. **Working Energy Consumption**

    $$e^{exe} = \beta \cdot f^3 \cdot t^{exe}$$

    - $\beta$: exe_energy_coef, energy consumption coefficient during working/computing state [Node]
        - $\alpha << \beta$
    - $t^{exe}$: task execution time
    - $f$: CPU frequency [Node]

### 2.3 More

<!-- Taking into account only waiting and execution, the delay and energy consumption of a task are calculated as follows:

- $$t = \frac{(q + d) \cdot c}{f}$$

- $$e = \beta \cdot f^3 \cdot t^{exe} = \beta \cdot f^3 \cdot \frac{d \cdot c}{f} = \beta \cdot f^2 \cdot d \cdot c$$ -->

- **From the perspective of tasks**, we usually focus on the response time, which is the waiting time plus the execution time, i.e., $t^{wait} + t^{exe}$.

- **From the perspective of nodes**, we emphasize working energy consumption $e^{exe}$ rather than idle energy consumption $e^{idle}$ (the latter is usually negligible by comparison). 