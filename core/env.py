import json
import os
import simpy
import networkx as nx

from typing import Optional, Tuple, List
from core.base_scenario import BaseScenario
from core.infrastructure import Link, Node
from core.task import Task

# Public interfaces
__all__ = ["EnvLogger", "Env"]

# Task status flags
FLAG_TASK_EXECUTION_DONE = 0
ENERGY_UNIT_CONVERSION = 1000


def user_defined_info(task):
    """ Define additional information for completed tasks, such as checking if the deadline is violated."""
    total_time = task.wait_time + task.exe_time
    return {'ddl_ok': total_time <= task.ddl}


class EnvLogger:
    """Logger for recording simulation events and key information."""

    def __init__(self, controller, enable_logging: bool = True, decimal_places: int = 3):
        self.controller = controller
        self.enable_logging = enable_logging  # Disable logging to speed up training
        self.decimal_places = decimal_places
        self.task_info: dict = {}  # Records task-related information
        self.node_info: dict = {}  # Records node-related information


    def log(self, message):
        """Log a message with a timestamp if logging is enabled."""
        if self.enable_logging:
            timestamp = f"{self.controller.now:.{self.decimal_places}f}"
            print(f"[{timestamp}]: {message}")

    def append(self, info_type: str, key: str, value: tuple) -> None:
        """
        Append key information to the logger.

        Args:
            info_type (str): Type of information ('task' or 'node').
            key (str): Task ID or Node ID.
            value (tuple): 
                - For 'task': (status_code, info_list, (src_name, dst_name))
                - For 'node': Energy consumption value.
        """
        if info_type not in ['task', 'node']:
            raise ValueError("info_type must be 'task' or 'node'")
        target_dict = self.task_info if info_type == 'task' else self.node_info
        target_dict[key] = value
        
    def get_value_idx(self, key: str) -> int:
        
        infos = ['status_code', 'node_names', 'time_list', 'energy_list']
        
        if key in infos:
            return infos.index(key)
        else:
            raise ValueError(f"Invalid key value: {key}")

    def reset(self) -> None:
        """Reset the logger by clearing all recorded information."""
        self.task_info.clear()
        self.node_info.clear()


class Env:
    """Simulation environment."""

    def __init__(self, scenario: BaseScenario, config_file: str, verbose: bool = True, 
                 decimal_places: int = 2):
        # Load configuration file
        with open(config_file, 'r') as file:
            self.config = json.load(file)
        self._validate_config()
            
        # Initialize simulation parameters
        self.refresh_rate = 1  # Typically, setting the refresh rate to 1 is OK.
        self.decimal_places = decimal_places
        self.scenario = scenario
        self.controller = simpy.Environment()
        self.logger = EnvLogger(self.controller, enable_logging=verbose, decimal_places=decimal_places)

        # Task and state management
        self.active_tasks: dict = {}  # Current active tasks
        self.done_task_info: list = []  # Information of completed tasks
        self.done_task_collector = simpy.Store(self.controller)
        self.task_count = 0  # Counter for processed tasks

        # self.processed_tasks = []  # for debug

        # Reset environment state
        self.reset()

        # Start monitoring process
        self.monitor_process = self.controller.process(self._monitor_done_task_collector())
        self.energy_recorders = {
            node.node_id: self.controller.process(self._track_node_energy(node))
            for node in self.scenario.get_nodes().values()
        }
        self.start_time = None

        # Start visualization frame recorder if enabled
        if self.config['Basic']['VisFrame'] == "on":
            self._setup_visualization_directories()
            self.frame_info: dict = {}
            self.frame_recorder = self.controller.process(self._record_frame_info())

    def _validate_config(self) -> None:
        """Validate configuration to ensure the number of tracked nodes does not exceed the limit."""
        max_nodes = 10
        target_nodes = len(self.config['VisFrame']['TargetNodeList'])
        assert target_nodes <= max_nodes, (
            f"Visualization layout limits tracked nodes to {max_nodes}. Modify layout to extend."
        )

    def _setup_visualization_directories(self) -> None:
        """Create directories for visualization logs and frames."""
        os.makedirs(self.config['VisFrame']['LogInfoPath'], exist_ok=True)
        os.makedirs(self.config['VisFrame']['LogFramesPath'], exist_ok=True)

    @property
    def now(self) -> float:
        """Get the current simulation time."""
        return self.controller.now
    
    @property
    def execution_time(self) -> float:
        """Get the current simulation time."""
        if self.start_time is None:
            return 0
        else:
            return self.controller.now - self.start_time

    def run(self, until: float) -> None:
        """Run the simulation until the specified time."""
        self.controller.run(until)

    def reset(self):
        """Reset the simulation environment."""
        # Interrupt all active tasks
        for task_process in self.active_tasks.values():
            if task_process.is_alive:
                task_process.interrupt()
        self.active_tasks.clear()
        self.task_count = 0

        # Reset scenario and logger
        self.scenario.reset()
        self.logger.reset()
        self.done_task_collector.items.clear()
        self.done_task_info.clear()

    def process(self, **kwargs):
        """Process a task using keyword arguments."""
        if self.start_time is None:
            self.start_time = self.now
        task_process = self._execute_task(**kwargs)
        self.controller.process(task_process)

    def _check_duplicate_task_id(self, task: Task, dst_name: Optional[str]):
        """
        Check if the task ID is duplicated, log the error and raise an exception if it is.

        Args:
            task (Task): The task to check.
            dst_name (Optional[str]): The destination node name.

        Raises:
            AssertionError: If the task ID is duplicated.
        """
        if task.task_id in self.active_tasks.keys():
            self.task_count += 1
            self.logger.append(info_type='task', 
                               key=task.task_id, 
                               value=(1, (task.src_name, dst_name), ['DuplicateTaskIdError'], [0,0]))
            log_info = f"**DuplicateTaskIdError: Task {{{task.task_id}}}** " \
                       f"new task (name {{{task.task_name}}}) with a " \
                       f"duplicate task id {{{task.task_id}}}."
            self.logger.log(log_info)
            raise AssertionError(('DuplicateTaskIdError', log_info, task.task_id))

    def _handle_task_transmission(self, task: Task, dst_name: str):
        """
        Handle the transmission logic of the task, including path calculation, error handling, and time simulation.

        Args:
            task (Task): The task to transmit.
            dst_name (str): The destination node name.

        Raises:
            EnvironmentError: If transmission fails due to network issues.
        """
        try:
            links_in_path = self.scenario.infrastructure.get_shortest_links(task.src_name, dst_name)
            task.links_in_path = links_in_path
        except nx.exception.NetworkXNoPath:
            self.task_count += 1
            self.logger.append(info_type='task', 
                               key=task.task_id, 
                               value=(1, (task.src_name, dst_name), ['NetworkXNoPathError'], [0,0]))
            log_info = f"**NetworkXNoPathError: Task {{{task.task_id}}}** Node {{{dst_name}}} is inaccessible"
            self.logger.log(log_info)
            raise EnvironmentError(('NetworkXNoPathError', log_info, task.task_id))
        except EnvironmentError as e:
            message = e.args[0]
            if message[0] == 'IsolatedWirelessNode':
                self.task_count += 1
                self.logger.append(info_type='task', 
                                   key=task.task_id, 
                                   value=(1, (task.src_name, dst_name), ['IsolatedWirelessNode'], [0,0]))   
                log_info = f"**IsolatedWirelessNode: Task {{{task.task_id}}}** Isolated wireless node detected"
                self.logger.log(log_info)
                raise e

        for link in links_in_path:
            if isinstance(link, Link) and link.free_bandwidth < task.trans_bit_rate:
                self.task_count += 1
                self.logger.append(info_type='task', 
                                   key=task.task_id, 
                                   value=(1, (task.src_name, dst_name), ['NetCongestionError'], [0,0]))
                log_info = f"**NetCongestionError: Task {{{task.task_id}}}** " \
                           f"network congestion Node {{{task.src_name}}} --> {{{dst_name}}}"
                self.logger.log(log_info)
                raise EnvironmentError(('NetCongestionError', log_info, task.task_id))

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

        self.scenario.send_data_flow(task.trans_flow, links_in_path)
        try:
            self.logger.log(f"Task {{{task.task_id}}}: {{{task.src_name}}} --> {{{dst_name}}}")
            yield self.controller.timeout(task.trans_time)
            task.trans_flow.deallocate()
            self.logger.log(f"Task {{{task.task_id}}} arrived Node {{{dst_name}}} with "
                            f"{{{task.trans_time:.{self.decimal_places}f}}}s")
        except simpy.Interrupt:
            pass

    def _execute_task_on_node(self, task: Task, dst, flag_reactive: bool):
        """
        Execute the task on the destination node, handling buffering and execution logic.

        Args:
            task (Task): The task to execute.
            dst: The destination node.
            flag_reactive (bool): Whether the task is from the waiting queue.

        Raises:
            EnvironmentError: If there is insufficient buffer space.
        """
        if not dst.free_cpu_freq > 0:
            try:
                task.allocate(self.now, dst, pre_allocate=True)
                dst.append_task(task)
                self.logger.log(f"Task {{{task.task_id}}} is buffered in Node {{{task.dst_name}}}")
                return
            except EnvironmentError as e:
                self.task_count += 1
                self.logger.append(info_type='task', 
                                   key=task.task_id, 
                                   value=(1, (task.src_name, task.dst_name), ['InsufficientBufferError'], [task.trans_energy, 0] ))
                self.scenario.get_node(task.dst_name).energy_consumption += task.exe_energy
                self.logger.log(e.args[0][1])
                raise e

        if flag_reactive:
            task.allocate(self.now)
            self.logger.log(f"Task {{{task.task_id}}} re-actives in Node {{{task.dst_name}}}, "
                            f"waiting {{{(task.wait_time - task.trans_time):.{self.decimal_places}f}}}s")
        else:
            task.allocate(self.now, dst)

        self.active_tasks[task.task_id] = task
        try:
            self.logger.log(f"Processing Task {{{task.task_id}}} in {{{task.dst_name}}}")
            yield self.controller.timeout(task.exe_time)
            self.done_task_collector.put(
                (task.task_id,
                 FLAG_TASK_EXECUTION_DONE,
                 [dst.name, user_defined_info(task)]))
        except simpy.Interrupt:
            pass

    def _execute_task(self, task: Task, dst_name: Optional[str] = None):
        """
        Handle the transmission and execution logic of the task.

        Args:
            task (Task): The task to execute.
            dst_name (Optional[str]): The destination node name. If None, the task is from the waiting queue.
        """
        # Check for duplicate task ID
        self._check_duplicate_task_id(task, dst_name)

        # Determine if the task is from the waiting queue
        flag_reactive = dst_name is None

        # Get the destination node
        dst = task.dst if flag_reactive else self.scenario.get_node(dst_name)

        if not flag_reactive:
            self.logger.log(f"Task {{{task.task_id}}} generated in Node {{{task.src_name}}}")

            if dst_name != task.src_name:
                # Handle task transmission
                yield from self._handle_task_transmission(task, dst_name)
            else:
                task.trans_time = 0  # No transmission needed

        # Execute the task on the node
        yield from self._execute_task_on_node(task, dst, flag_reactive)

    def _monitor_done_task_collector(self):
        """Monitor the done_task_collector queue to process completed tasks."""
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
                        
                        self.scenario.get_node(task.dst_name).energy_consumption += task.exe_energy + task.trans_energy
                        

                        # Log task completion with execution time
                        self.logger.log(f"Task {{{task_id}}}: Accomplished in "
                                        f"Node {{{task.dst_name}}} with "
                                        f"execution time {{{task.exe_time:.{self.decimal_places}f}}}s")

                        # Record task statistics (success, times, node names)
                        self.logger.append(info_type='task', 
                                           key=task.task_id, 
                                           value=(0,                                                  
                                            (task.src_name, task.dst_name),
                                            [task.trans_time, task.wait_time, task.exe_time], 
                                            [task.trans_energy, task.exe_energy])
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
            yield self.controller.timeout(self.refresh_rate)
    
    def _track_node_energy(self, node: Node):
        """Recorder of node's energy consumption."""
        while True:
            node.energy_consumption += node.idle_energy_coef * self.refresh_rate * node.max_cpu_freq
            # node.energy_consumption += node.exe_energy_coef * (
            #     node.max_cpu_freq - node.free_cpu_freq) * self.refresh_rate
            node.total_cpu_freq += (node.max_cpu_freq - node.free_cpu_freq) * self.refresh_rate
            yield self.controller.timeout(self.refresh_rate)
    
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
            yield self.controller.timeout(self.refresh_rate)

    @property
    def n_active_tasks(self) -> int:
        """Get the number of currently active tasks."""
        return len(self.active_tasks)

    def status(self, node_name: Optional[str] = None, link_args: Optional[Tuple] = None) -> any:
        """Retrieve the status of a node or link."""
        return self.scenario.status(node_name, link_args)
    
    def avg_node_energy(self, node_name_list: Optional[List[str]] = None, power=False) -> float:
        """Calculate the average energy consumption across specified nodes."""
        if power:
            return self.scenario.avg_node_energy(node_name_list) / (self.execution_time + 1e-6)
        else:
            return self.scenario.avg_node_energy(node_name_list) / ENERGY_UNIT_CONVERSION
    
    def node_energy(self, node_name: str, power=False) -> float:
        """Retrieve the energy consumption of a specific node."""
        if power:
            return self.scenario.node_energy(node_name) / (self.execution_time + 1e-6) 
        else:
            return self.scenario.node_energy(node_name) / ENERGY_UNIT_CONVERSION

    def close(self):
        # Log energy consumption and CPU frequency per clock cycle for each node
        for _, node in self.scenario.get_nodes().items():
            self.logger.append(info_type='node', 
                               key=node.node_id, 
                               value=[
                                   node.energy_consumption,  # Average energy per cycle
                                   node.total_cpu_freq       # Average CPU frequency
                               ])
        
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
        if self.config['Basic']['VisFrame'] == "on":
            self.frame_recorder.interrupt()

        # --- Log Completion ---
        # Record simulation completion
        self.logger.log("Simulation completed!")
