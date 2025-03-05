"""
================================================================================
Dataset Information
================================================================================
This simulation uses a real IoT compute dataset, originally available at:
    https://github.com/saifulislamPhD/IoT-Compute-Dataset

Each dataset entry typically includes fields such as:
    TaskName, GenerationTime, TaskID, TaskSize, CyclesPerBit, TransBitRate,
    DDL, DataType, DeviceType

Example row (CSV format):
    t0,0.0,0,270,1000.0,100,30,Bulk,Mobile

- TaskName:      A unique identifier for the task.
- GenerationTime:Time at which the task is created (in seconds).
- TaskID:        Numeric ID of the task, unique across the dataset.
- TaskSize:      Input data size in kilobytes (MB).
- CyclesPerBit:  The CPU cycles needed per bit of task data.
- TransBitRate:  Transfer bit rate (in mbps) used when offloading the task.
- DDL:           Deadline (in seconds), the max wait time from generation to start.
- DataType:      Category of the data (e.g., Bulk, Video, Sensor).
- DeviceType:    Class of the generating device (e.g., Mobile, SensorNode).

Some adjustments (e.g., unit scaling or approximate conversions) may be performed
to align these fields with the particular needs and constraints of the simulation.

================================================================================
Scenario Information
================================================================================

In this simulation scenario, we model a set of nodes (Edge, Fog, and Cloud) as 
defined in a JSON structure. Each node entry includes resource attributes such 
as CPU frequency (cpu_freq), buffer size, and energy coefficients, as well as 
its geographic location. Edges represent network links with specified bandwidth 
capacities in kilobits per second (kbps).

------------------------------------------------------------------------------
1. CPU Frequency (cpu_freq in MIPS)
------------------------------------------------------------------------------
    - MIPS translates to "thousands of instructions per second."
    - The value represents the product of (number_of_cores) * (frequency_per_core).
      For example, if a node has 4 cores, each running at 2,500 instructions per 
      second, then:
          cpu_freq = 4 * 2,500 = 10,000 MIPS
      This means the node can handle 10,000  million instructions 
      per second in total.

------------------------------------------------------------------------------
2. Node Definition (JSON Example)
------------------------------------------------------------------------------
  "Nodes": [
    {
      "DeviceType": "Edge",
      "NodeType": "Node",
      "NodeName": "e0",
      "NodeId": 0,
      "MaxCpuFreq": 10000,
      "MaxBufferSize": 4096,
      "IdleEnergyCoef": 0.01,
      "ExeEnergyCoef": 0.4,
      "LocX": 33.68742,
      "LocY": 73.0078,
      "Location": "Islamabad, Pakistan"
    },
    ...
  ]

  - DeviceType:      Denotes whether the node is Edge, Fog, or Cloud.
  - NodeType:        Usually set to "Node" for identification in the simulator.
  - NodeName:        A unique string label (e.g., "e0", "f1", "c0").
  - NodeId:          Unique integer identifier for referencing this node.
  - MaxCpuFreq:      Maximum CPU frequency in MIPS (thousands of instructions 
                     per second). Reflects aggregated core frequencies.
  - MaxBufferSize:   The maximum number of tasks size in MB (or size of task queue) that can 
                     be held at this node before new tasks are dropped.
  - IdleEnergyCoef:  Coefficient indicating the node's power consumption during 
                     idle periods (no active tasks) in Watts.
  - ExeEnergyCoef:   Coefficient indicating the node's power consumption rate 
                     while actively executing tasks in Watts.
  - LocX, LocY:      Geographic coordinates (latitude/longitude) in decimal 
                     degrees.
  - Location:        Human-readable location (e.g., "Islamabad, Pakistan").

------------------------------------------------------------------------------
3. Edge (Network Link) Definition (JSON Example)
------------------------------------------------------------------------------
  "Edges": [
    {
      "EdgeType": "SingleLink",
      "SrcNodeID": 0,
      "DstNodeID": 1,
      "Bandwidth": 2500
    },
    ...
  ]

  - EdgeType:    Indicates the kind of link (e.g., "SingleLink", "Link").
  - SrcNodeID:   Integer ID of the source node in the network.
  - DstNodeID:   Integer ID of the destination node.
  - Bandwidth:   The maximum link capacity in megabits per second (mbps). Actual
                 throughput may be lower depending on congestion, scheduling, 
                 and the number of concurrent data flows.

------------------------------------------------------------------------------
4. Adaptations and Use Case
------------------------------------------------------------------------------
While this format closely follows the original dataset structure, some numerical 
values (like buffer sizes, CPU frequencies, and bandwidths) have been adjusted 
to create a more realistic and manageable simulation scenario. These resources 
represent a heterogeneous environment where Edge nodes have limited capabilities, 
Fog nodes serve as intermediate micro data centers, and Cloud nodes provide high 
computational power at the cost of higher idle energy and increased latency.

Together, these definitions enable the simulation to test various offloading 
strategies—evaluating how tasks should be distributed among Edge, Fog, and Cloud 
layers to balance energy consumption, responsiveness (latency), and task throughput.

Sources:
  - M. M. Bukhari et al., “An Intelligent Proposed Model for Task Offloading in 
    Fog-Cloud Collaboration Using Logistic Regression,” Computational Intelligence 
    and Neuroscience, 2022.
  - M. Aazam et al., “Cloud of Things (CoT): Cloud-Fog-IoT Task Offloading for 
    Sustainable Internet of Things,” IEEE Transactions on Sustainable Computing, 
    2022.
"""