<div style="text-align: center;">
  <img src="https://github.com/ZhangRui111/RayCloudSim/blob/main/docs/imgs/logo_long.jpg" alt="" width="800"/>
</div>

# RayCloudSim

Note: This README file is recommended to be viewed with a reader that supports LaTeX.

## 1. Attribute Modeling

1. **Node**:
    - *id*: Node ID, unique identifier.
    - *name*: The human-readable name of the node.
    - *max_cpu_freq*: The maximum CPU frequency of the node.
    - *free_cpu_freq* (float): The current available CPU frequency.
    - *task_buffer*: A FIFO buffer for tasks that are waiting to be processed.
    - *location*: The geographical location of the node.
    - *energy_coefficients*: A dictionary containing energy consumption coefficients for different states.
    - *energy_consumption*: The total energy consumed by the node.

2. **Link**:
    - *src*: The source node of the link.
    - *dst*: The destination node of the link.
    - *max_bandwidth*: The maximum bandwidth of the link.
    - *free_bandwidth*: The current available bandwidth of the link.
    - *dis*: The distance between the source and destination nodes.
    - *base_latency*: The base latency of the link, useful for routing policies.
    - *data_flows*: A list of DataFlow objects currently allocated on this link.

3. **Task**:
    - *id*: Task ID, unique identifier.
    - *task_size*: Size of the task.
    - *cycles_per_bit*: Number of CPU cycles per bit of task data.
    - *trans_bit_rate*: Transmission bit rate for the task.
    - *ddl*: Maximum tolerable time (deadline).
        The default value for *ddl* is -1, indicating that the user does not consider the task to have a deadline requirement.
    - *cpu_freq*: CPU frequency during execution.

    - *trans_time*: Task transmission time. If the destination node of the task is the same as the source node, then *trans_time* = 0.
    - *wait_time*: Task queuing time. If the task does not need to be queued, then *wait_time* = 0.
    - *exe_time*: Task execution time at the destination node.
        The total response time of the task = *trans_time* + *wait_time* + *exe_time*. Note that, currently, the return time of the task result is not considered, as the size of the task result is typically small.

## 2. Dynamic Modeling

Here, [ ] indicates that the value depends on what it is related to.

### 2.1 Time

1. **Transmission Time**

    $$t^{trans} = \frac{d}{B} \cdot n$$

    - $d$: task size in bits **[Task]**
    - $B$: bandwidth **[Link]**
    - $n$: multi-hop routing **[Link/System]**

2. **Waiting Time**

    $$t^{wait} = \frac{q \cdot c}{f}$$

    - $q$: total size of all queued tasks preceding the current task **[Task]**
    - $c$: amount of CPU cycles per bit **[Task]**
    - $f$: CPU frequency **[Node]**

3. **Execution Time**

    $$t^{exe} = \frac{d \cdot c}{f}$$

### 2.2 Energy Consumption

1. **Idling**

    $$e^{idle} = \alpha \cdot t^{idle}$$

    - $\alpha$: idle_energy_coef, energy consumption coefficient during idle state **[Node]**
    - $t^{idle}$: idle time

2. **Working**

    $$e^{exe} = \beta \cdot f^3 \cdot t^{exe}$$

    - $\beta$: exe_energy_coef, energy consumption coefficient during working/computing state **[Node]**
        - $\alpha << \beta$
    - $t^{exe}$: task execution time
    - $f$: CPU frequency **[Node]**
