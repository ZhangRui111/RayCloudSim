import json
import networkx as nx
import os
import simpy
from typing import Optional, Tuple, List

from core.base_scenario import BaseScenario
from core.link import Link
from core.node import Node
from core.task import Task

__all__ = ["EnvLogger", "Env"]

FLAG_TASK_EXECUTION_DONE = 0
ENERGY_UNIT_CONVERSION = 1e6


def user_defined_info(task: Task) -> dict:
    """Define additional information for completed tasks.

    This function can be customized to include specific metrics or checks relevant to 
    the simulation scenario, such as checking if the task met its deadline.
    """
    # Calculate the total time taken for the task
    total_time = task.trans_time + task.wait_time + task.exe_time
    # Check if the total time is within the task's deadline
    if task.ddl == -1:     # -1 is the default value, indicating that the user does not
        ddl_ok_val = True  # consider the task to have a deadline requirement.
    else:
        ddl_ok_val = total_time <= task.ddl
    return {"ddl_ok": ddl_ok_val}


class EnvLogger:
    """Logger for recording simulation events and key information.

    This class is used to capture details about task processing, node status,
    and other relevant events during the simulation run.
    """

    def __init__(self, controller: simpy.Environment, enable_logging: bool = True):
        """
        Initializes the EnvLogger.

        Args:
            controller: The SimPy environment controller.
            enable_logging: A boolean indicating whether logging is enabled.
                            Disabling logging can shorten simulation's wall-clock time.
        """
        self.controller = controller
        self.enable_logging = enable_logging  # Disable logging can speed up simulation
        
        self.task_info: dict = {}  # Records task-related information
        self.node_info: dict = {}  # Records node-related information

    def log(self, message: str):
        """Log a message with the current simulation timestamp if logging is enabled."""
        if self.enable_logging:
            print(f"[{self.controller.now:.2f}]: {message}")
    
    def append(self, info_type: str, key: str, value: tuple) -> None:
        """Append key information to the logger.

        Args:
            info_type (str): Type of information ('task' or 'node').
            key (str): Task ID or Node ID.
            value (tuple):
                - For 'task': (status_code, info_list, (src_name, dst_name))
                             status_code: 0 for success, 1 for failure.
                             info_list: List of relevant information (e.g., times, error type).
                             (src_name, dst_name): Tuple of source and destination node names.
                - For 'node': Energy consumption value.
        """
        if info_type not in ['task', 'node']:
            raise ValueError("info_type must be 'task' or 'node'")

        target_dict = self.task_info if info_type == 'task' else self.node_info
        target_dict[key] = value

    def reset(self) -> None:
        """Reset the logger by clearing all recorded information."""
        self.task_info.clear()
        self.node_info.clear()


class Env:
    """Simulation environment for RayCloudSim.

    This class manages the simulation flow, including task processing, resource allocation, 
    and event logging, based on a given scenario and configuration.
    """

    def __init__(self, scenario: BaseScenario, config_file: str, enable_logging: bool = True):
        """Initializes the simulation environment.

        Args:
            scenario: The BaseScenario object defining the simulation scenario.
            config_file: The path to the JSON configuration file for the environment.
            enable_logging: A boolean indicating whether logging is enabled.
        """
        # Load configuration file
        with open(config_file, 'r') as file:
            self.config = json.load(file)
        self._validate_config()
            
        # Initialize simulation parameters
        self.scenario = scenario
        self.controller = simpy.Environment()  # SimPy environment controller
        self.logger = EnvLogger(self.controller, enable_logging=enable_logging) # Logger

        # Task and state management
        self.active_tasks: dict = {}  # Dictionary to store currently active tasks (id: Task)
        self.done_task_info: list = []  # List to store information of completed tasks

        # SimPy Store to collect information about completed tasks
        self.done_task_collector = simpy.Store(self.controller)
        self.task_count = 0  # Counter for the total number of processed tasks

        # self.processed_tasks = []  # for debug

        # Reset environment state
        self.reset()

        # Start the process that monitors the done_task_collector
        self.monitor_process = self.controller.process(self._monitor_done_task_collector())

        # Start energy tracking processes for each node
        self.energy_recorders = {
            node.id: self.controller.process(self._track_node_energy(node))
            for node in self.scenario.get_nodes().values()
        }

        # Start visualization frame recorder if enabled
        if self.config['Basic']['VisFrame'] == "on":
            os.makedirs(self.config['VisFrame']['LogInfoPath'], exist_ok=True)
            os.makedirs(self.config['VisFrame']['LogFramesPath'], exist_ok=True)
            self.frame_info: dict = {}
            self.frame_recorder = self.controller.process(self._record_frame_info())

    def _validate_config(self) -> None:
        """Validate configuration to ensure the number of tracked nodes does not exceed the limit."""
        max_nodes = 10
        target_nodes = len(self.config['VisFrame']['TargetNodeList'])
        assert target_nodes <= max_nodes, (
            f"Visualization layout limits tracked nodes to {max_nodes}. Modify layout to extend."
        )

    @property
    def now(self) -> float:
        """Get the current simulation time."""
        return self.controller.now

    @property
    def n_active_tasks(self) -> int:
        """Get the number of currently active tasks."""
        return len(self.active_tasks)

    def status(self, node_name: Optional[str] = None, link_args: Optional[Tuple] = None) -> any:
        """Retrieve the status of a specific node or link from the scenario."""
        return self.scenario.status(node_name, link_args)

    def run(self, until: float):
        """Run the simulation until the specified time.

        Args:
            until: The simulation time to run until.
        """
        self.controller.run(until)

    def process(self, **kwargs):
        """Initiate the processing of a task.

        This method creates a SimPy process for handling a task's transmission
        and execution and schedules it in the simulation environment.

        Args:
            **kwargs: Keyword arguments to be passed to the _process_task method,
                      typically including the 'task' object.
        """
        # Create a SimPy process for the task
        task_process = self._process_task(**kwargs)
        # Schedule the process in the simulation environment
        self.controller.process(task_process)

    def _process_task(self, task: Task, dst_name: Optional[str] = None):
        """Handle the transmission and execution of the task.

        This is a generator function that yields SimPy events to simulate
        the passage of time during transmission and execution.

        Args:
            task (Task): The task to execute.
            dst_name (Optional[str]): The destination node name. If None, the task is from 
                                      the waiting queue.
        """
        # Check for duplicate task ID to prevent errors
        if task.id in self.active_tasks.keys():
            # If task ID is already in active tasks, it's a duplicate
            self.task_count += 1 # Increment task count for the failed task
            self.logger.append(
                info_type='task',
                key=task.id,
                value=(1, ['DuplicateTaskIdError'], (task.src_name, dst_name))
            )
            log_info = f"**DuplicateTaskIdError: Task {{{task.id}}}** " \
                       f"new task (name {{{task.task_name}}}) with a " \
                       f"duplicate task id {{{task.id}}}."
            self.logger.log(log_info) # Log the error message
            raise AssertionError(('DuplicateTaskIdError', log_info, task.id)) # Raise assertion error

        # Determine if the task is from the waiting queue
        flag_reactive = dst_name is None

        # Get the destination node
        dst = task.dst if flag_reactive else self.scenario.get_node(dst_name)

        if not flag_reactive:
            self.logger.log(f"Task {{{task.id}}} generated in Node {{{task.src_name}}}")

            if dst_name != task.src_name:
                # Handle task transmission
                yield from self._handle_task_transmission(task, dst_name)
            else:
                task.trans_time = 0  # No transmission needed

        # Execute the task on the node
        yield from self._handle_task_execution(task, dst, flag_reactive)

    def _handle_task_transmission(self, task: Task, dst_name: str):
        """Handle the transmission of the task from its source to the destination node.

        This includes calculating the path, simulating transmission time based on
        bandwidth and latency, and handling potential network errors.

        Args:
            task (Task): The task to transmit.
            dst_name (str): The name of the destination node.

        Yields:
            SimPy timeout events to simulate transmission time.

        Raises:
            EnvironmentError: If transmission fails due to network issues (e.g., no path, 
                              congestion).
        """
        try:
            # Get the shortest path as a list of links between source and destination
            links_in_path = self.scenario.infrastructure.get_shortest_links(
                task.src_name, dst_name)
        except nx.exception.NetworkXNoPath:
            # Handle case where no path exists between the nodes
            self.task_count += 1
            self.logger.append(
                info_type='task',
                key=task.id,
                value=(1, ['NetworkXNoPathError'], (task.src_name, dst_name)),
            )
            log_info = (
                f"**NetworkXNoPathError: Task {{{task.id}}}** "
                f"Node {{{dst_name}}} is inaccessible"
            )
            self.logger.log(log_info)
            raise EnvironmentError(('NetworkXNoPathError', log_info, task.id))
        except EnvironmentError as e:
            message = e.args[0]
            if message[0] == 'IsolatedWirelessNode':
                self.task_count += 1
                self.logger.append(
                    info_type='task', 
                    key=task.id, 
                    value=(1, ['IsolatedWirelessNode'], (task.src_name, dst_name)),
                )
                log_info = f"**IsolatedWirelessNode: Task {{{task.id}}}** Isolated wireless node detected"
                self.logger.log(log_info)
                raise e

        # Check for network congestion along the path
        for link in links_in_path:
            if isinstance(link, Link) and link.free_bandwidth < task.trans_bit_rate:
                # Handle case where there is not enough free bandwidth on a link
                self.task_count += 1
                self.logger.append(
                    info_type='task',
                    key=task.id,
                    value=(1, ['NetCongestionError'], (task.src_name, dst_name))
                )
                log_info = f"**NetCongestionError: Task {{{task.id}}}** " \
                           f"network congestion Node {{{task.src_name}}} --> {{{dst_name}}}"
                self.logger.log(log_info)
                raise EnvironmentError(('NetCongestionError', log_info, task.id))

        # Calculate transmission time
        task.trans_time = 0

        # Wireless transmission (first hop)
        if isinstance(links_in_path[0], Tuple):
            wireless_src_name, wired_dst_name = links_in_path[0]
            task.trans_time += 0  # Placeholder, to be implemented with actual calculation
            links_in_path = links_in_path[1:]

        # Wireless transmission (last hop)
        if isinstance(links_in_path[-1], Tuple):
            wired_src_name, wireless_dst_name = links_in_path[-1]
            task.trans_time += 0  # Placeholder, to be implemented with actual calculation
            links_in_path = links_in_path[:-1]

        # Wired transmission: base latency and multi-hop delay
        trans_base_latency = 0
        for link in links_in_path:
            trans_base_latency += link.base_latency
        task.trans_time += trans_base_latency
        task.trans_time += (task.task_size / task.trans_bit_rate) * len(links_in_path)

        # Allocate the data flow to the links in the path
        self.scenario.send_data_flow(task.trans_flow, links_in_path)
        try:
            # Log the start of transmission and yield a timeout for the transmission time
            self.logger.log(f"Task {{{task.id}}}: {{{task.src_name}}} --> {{{dst_name}}}")
            yield self.controller.timeout(task.trans_time)
            # Deallocate the data flow after transmission is complete
            task.trans_flow.deallocate()
            self.logger.log(f"Task {{{task.id}}} arrived Node {{{dst_name}}} with "
                            f"{{{task.trans_time:.2f}}}s")
        except simpy.Interrupt:
            # Handle interruption during transmission (e.g., due to environment reset)
            pass

    def _handle_task_execution(self, task: Task, dst, flag_reactive: bool):
        """Handle the execution of the task on the destination node.

        This includes checking for available CPU resources, handling buffering
        if necessary, simulating execution time, and processing task completion.

        Args:
            task (Task): The task to execute.
            dst: The destination node where the task will be executed.
            flag_reactive (bool): A flag indicating if the task is being reactivated
                                  from a waiting queue (True) or is a newly arrived task (False).

        Yields:
            SimPy timeout events to simulate execution time.

        Raises:
            EnvironmentError: If there is insufficient buffer space to queue the task.
        """
        # Check if the destination node has free CPU resources
        if not dst.free_cpu_freq > 0:
            try:
                # If no free CPU, attempt to buffer the task
                task.allocate(self.now, dst, pre_allocate=True) # Pre-allocate resources if possible
                dst.append_task(task) # Append task to the node's buffer
                self.logger.log(f"Task {{{task.id}}} is buffered in Node {{{task.dst_name}}}")
                return # Task is buffered, execution will happen later
            except EnvironmentError as e:
                # Handle insufficient buffer space error
                self.task_count += 1
                self.logger.append(
                    info_type='task',
                    key=task.id,
                    value=(1, ['InsufficientBufferError'], (task.src_name, task.dst_name)),
                )
                self.logger.log(e.args[0][1]) # Log the specific error message
                raise e # Re-raise the exception

        # If CPU is free, allocate resources and proceed with execution
        if flag_reactive:
            # If reactive, allocate resources at the current time
            task.allocate(self.now)
            self.logger.log(f"Task {{{task.id}}} re-actives in Node {{{task.dst_name}}}, "
                            f"waiting {{{task.wait_time:.2f}}}s")
        else:
            # If not reactive, allocate resources on the destination node
            task.allocate(self.now, dst)

        # Add the task to the list of active tasks on the node
        self.active_tasks[task.id] = task
        try:
            # Log the start of execution and yield a timeout for the execution time
            self.logger.log(f"Processing Task {{{task.id}}} in {{{task.dst_name}}}")
            yield self.controller.timeout(task.exe_time)
            # If execution completes without interruption, put task info in the collector
            self.done_task_collector.put(
                (task.id,
                 FLAG_TASK_EXECUTION_DONE,
                 [dst.name, user_defined_info(task)]))
        except simpy.Interrupt:
            # Handle interruption during execution (e.g., due to environment reset)
            pass

    def _monitor_done_task_collector(self):
        """Monitor the done_task_collector queue to process completed tasks.

        This is a continuous SimPy process that wakes up periodically to check
        for tasks that have finished execution and processes their completion.
        """
        while True:
            # --- Check for Completed Tasks ---
            if len(self.done_task_collector.items) > 0:
                while len(self.done_task_collector.items) > 0:
                    task_id, flag, info = self.done_task_collector.get().value
                    self.done_task_info.append((self.now, task_id, flag, info))

                    if flag == FLAG_TASK_EXECUTION_DONE:
                        # Retrieve the task from active tasks
                        task = self.active_tasks[task_id]

                        # Pop the next task from the destination node's waiting queue
                        waiting_task = task.dst.pop_task()

                        # Log task completion with execution time
                        self.logger.log(f"Task {{{task_id}}}: Accomplished in "
                                        f"Node {{{task.dst_name}}} with "
                                        f"execution time {{{task.exe_time:.2f}}}s")

                        # Record task statistics (success, times, node names) in the logger
                        self.logger.append(
                            info_type='task',
                            key=task.id,
                            value=(
                                0, 
                                [task.trans_time, task.wait_time, task.exe_time], 
                                (task.src_name, task.dst_name)
                            ),
                        )
                        
                        # Clean up: deallocate resources and remove from active tasks
                        task.deallocate()
                        del self.active_tasks[task_id]
                        self.task_count += 1
                        # self.processed_tasks.append(task.task_id)

                        # Process the next waiting task if it exists
                        if waiting_task:
                            self.process(task=waiting_task)

                    else:
                        # Handle invalid task flag with detailed error
                        raise ValueError(f"Invalid flag '{flag}' encountered for task {task_id}")
            
            # --- Reset for Next Cycle ---
            else:
                self.done_task_info = []
                # self.logger.log("")  # turn on: log on every time slot

            # Pause execution until the next refresh interval
            yield self.controller.timeout(1)

    def reset(self):
        """Reset the simulation environment to its initial state.

        This includes interrupting active tasks, clearing task and logger information,
        and resetting the scenario.
        """
        # Interrupt all active tasks to stop their processes
        for task_process in self.active_tasks.values():
            if task_process.is_alive:
                task_process.interrupt()
        self.active_tasks.clear() # Clear the dictionary of active tasks
        self.task_count = 0 # Reset the processed task counter

        # Reset the scenario and the logger
        self.scenario.reset()
        self.logger.reset()
        # Clear the done task collector and the list of completed task info
        self.done_task_collector.items.clear()
        self.done_task_info.clear()

    def close(self):
        """Clean up and finalize the simulation environment.

        This includes logging final energy consumption and CPU frequency metrics,
        and terminating active SimPy processes.
        """
        # Log energy consumption and CPU frequency per clock cycle for each node
        for _, node in self.scenario.get_nodes().items():
            # Append node metrics to the logger
            self.logger.append(
                info_type='node',
                key=node.id,
                value=[
                    node.energy_consumption / node.clock if node.clock > 0 else 0,  # Average energy per cycle
                    node.total_cpu_freq / node.clock if node.clock > 0 else 0       # Average CPU frequency
                ],
            )
        
        # --- Save Visualization Data ---
        # Save frame info to JSON if visualization is enabled
        if self.config['Basic']['VisFrame'] == "on":
            frame_info_json_object = json.dumps(self.frame_info, indent=4)
            with open(f"{self.config['VisFrame']['LogInfoPath']}/frame_info.json", 'w+') as fw:
                fw.write(frame_info_json_object)

        # --- Terminate Processes ---
        # Interrupt the monitoring process
        self.monitor_process.interrupt()

        # Interrupt all active energy recorders and clear the collection
        for p in self.energy_recorders.values():
            if p.is_alive:
                p.interrupt()
        self.energy_recorders.clear()

        # Interrupt frame info recorder if visualization is enabled
        try:
            if self.config['Basic']['VisFrame'] == "on":
                self.frame_recorder.interrupt()
        except RuntimeError as e:
            self.logger.log(e)

        # --- Log Completion ---
        # Record simulation completion
        self.logger.log("Simulation completed!")

    def _track_node_energy(self, node: Node):
        """SimPy process to track a node's energy consumption over time.

        This process runs continuously and updates the node's energy consumption
        and total CPU frequency usage based on its current state.

        Args:
            node: The Node object to track.

        Yields:
            SimPy timeout events to advance the simulation time.
        """
        while True:
            # Update energy consumption based on idle and execution coefficients
            node.energy_consumption += node.energy_coefficients['idle']
            node.energy_consumption += node.energy_coefficients['exe'] * (
                node.max_cpu_freq - node.free_cpu_freq) ** 3 # Example energy model (cubic)
            # Accumulate total CPU frequency used
            node.total_cpu_freq += node.max_cpu_freq - node.free_cpu_freq
            node.clock += 1 # Increment the node's internal clock
            # Yield a timeout to simulate the passage of 1 simulation time unit
            yield self.controller.timeout(1)
    
    def _record_frame_info(self):
        """Record simulation frame information at regular intervals."""
        while True:
            # Collect node and edge status at the current time
            self.frame_info[self.now] = {
                'node': {k: item.quantify_cpu_freq() 
                         for k, item in self.scenario.get_nodes().items()},
                'edge': {str(k): item.quantify_bandwidth() 
                         for k, item in self.scenario.get_links().items()},
            }
            # Include target node details if specified in config
            if len(self.config['VisFrame']['TargetNodeList']) > 0:
                self.frame_info[self.now]['target'] = {
                    item: [
                        self.scenario.get_node(item).active_task_ids[:], 
                        self.scenario.get_node(item).task_buffer.task_ids[:]
                    ]
                    for item in self.config['VisFrame']['TargetNodeList']
                }
            # Wait for the next refresh cycle
            yield self.controller.timeout(1)
    
    def avg_node_energy(self, node_name_list: Optional[List[str]] = None) -> float:
        """Calculate the average energy consumption across specified nodes."""
        # Get average energy from the scenario and convert units
        return self.scenario.avg_node_energy(node_name_list) / ENERGY_UNIT_CONVERSION

    def node_energy(self, node_name: str) -> float:
        """Retrieve the energy consumption of a specific node."""
        # Get node energy from the scenario and convert units
        return self.scenario.node_energy(node_name) / ENERGY_UNIT_CONVERSION
