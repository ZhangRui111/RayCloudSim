import json
import os
import simpy
import networkx as nx
import math
import warnings
import json

from typing import Optional, Tuple

from core.base_scenario import BaseScenario
from core.infrastructure import Link
from core.task import Task

__all__ = ["EnvLogger", "Env"]

# Flag for completed task execution.
FLAG_TASK_EXECUTION_DONE = 0

def user_defined_info():
    """User can extend completed-task info here."""
    return None

class EnvLogger:
    def __init__(self, controller, is_open=True):
        self.controller = controller
        self.is_open = is_open  # Set to False to disable logging and speed up simulation.
        self.task_info = {}
        self.node_info = {}
        self.lastest_task_info = {}

    def log(self, content):
        if self.is_open:
            # env.now is in simulation time units (ms); we convert to seconds.
            sim_time = self.controller.now / self.controller.time_scale
            print(f"[{sim_time:.3f}]: {content}")

    def append(self, info_type, key, val):
        """Record key info during simulation.
        
        Args:
            info_type: 'task' or 'node'
            key: task id or node id
            val: For tasks, a tuple (code, info list); for nodes, typically energy consumption.
        """
        assert info_type in ['task', 'node']
        if info_type == 'task':
            self.task_info[key] = val
        else:
            self.node_info[key] = val

    def reset(self):
        self.task_info = {}
        self.node_info = {}

    def get_last_task_info(self):
        return self.task_info

class Env:
    def __init__(self, scenario: BaseScenario, config_file, verbose=True, refresh_rate: float = 1.0):
        """
        Initializes the simulation environment.
        
        Args:
            scenario: An instance of your scenario.
            config_file: Path to the configuration JSON.
            verbose: If True, logger prints messages.
            refresh_rate: Time interval (in seconds) for background actualization.
                          E.g., 0.01 corresponds to 10 ms.
        """
        with open(config_file, 'r') as fr:
            self.config = json.load(fr)
        assert len(self.config['VisFrame']['TargetNodeList']) <= 10, (
            "For visualization, the default number of tracked nodes does not exceed ten."
        )
        
        self.scenario = scenario
        self.controller = simpy.Environment()
        # Set time_scale: 1 s = 1000 simulation time units (ms)
        self.controller.time_scale = 1000
        self.refresh_rate = refresh_rate  # refresh_rate in seconds (e.g., 0.01 s = 10 ms)
        self.logger = EnvLogger(self.controller, is_open=verbose)

        self.active_task_dict = {}  # currently active tasks
        self.done_task_info = []    # completed task info (list of tuples)
        self.done_task_collector = simpy.Store(self.controller)
        self.process_task_cnt = 0

        self.reset()

        # Launch background processes:
        self.monitor_process = self.controller.process(self.monitor_on_done_task_collector())
        
        self.energy_recorders = {}
        for _, node in self.scenario.get_nodes().items():
            self.energy_recorders[node.node_id] = self.controller.process(self.energy_clock(node))
        
        if self.config['Basic']['VisFrame'] == "on":
            os.makedirs(self.config['VisFrame']['LogInfoPath'], exist_ok=True)
            os.makedirs(self.config['VisFrame']['LogFramesPath'], exist_ok=True)
            self.info4frame = {}
            self.info4frame_recorder = self.controller.process(self.info4frame_clock())

    @property
    def now(self):
        """Return current simulation time in seconds (with ms resolution)."""
        return self.controller.now / self.controller.time_scale

    def run(self, until):
        """Run the simulation until time 'until' (in seconds)."""
        self.controller.run(until=until * self.controller.time_scale)

    def reset(self):
        """Reset the Env: clear tasks, buffers, logs, etc."""
        for p in self.active_task_dict.values():
            if p.is_alive:
                p.interrupt()
        self.active_task_dict.clear()
        self.process_task_cnt = 0
        self.scenario.reset()
        self.logger.reset()
        self.done_task_collector.items.clear()
        del self.done_task_info[:]

    def process(self, **kwargs):
        """Start processing a task by scheduling its execution."""
        task_generator = self.execute_task(**kwargs)
        self.controller.process(task_generator)

    def execute_task(self, task: Task, dst_name=None):
        """
        Execute task transmission and execution.
        If dst_name is not provided, the task is re-activated from queuing.
        """
        if task.task_id in self.active_task_dict.keys():
            self.process_task_cnt += 1
            self.logger.append(info_type='task', key=task.task_id, val=(1, ['DuplicateTaskIdError',]))
            self.logger.log(f"**DuplicateTaskIdError: Task {{{task.task_id}}}** new task (name {{{task.task_name}}}) with duplicate task id {{{task.task_id}}}.")
            raise AssertionError(('DuplicateTaskIdError', task.task_id))
        
        flag_reactive = (dst_name is None)

        if flag_reactive:
            dst = task.dst
        else:
            self.logger.log(f"Task {{{task.task_id}}} generated in Node {{{task.src_name}}}")
            dst = self.scenario.get_node(dst_name)

        if not flag_reactive:
            if dst_name != task.src_name:
                try:
                    links_in_path = self.scenario.infrastructure.get_shortest_links(task.src_name, dst_name)
                except nx.exception.NetworkXNoPath:
                    self.process_task_cnt += 1
                    self.logger.append(info_type='task', key=task.task_id, val=(1, ['NetworkXNoPathError',]))
                    self.logger.log(f"**NetworkXNoPathError: Task {{{task.task_id}}}** Node {{{dst_name}}} is inaccessible")
                    raise EnvironmentError(('NetworkXNoPathError', task.task_id))
                except EnvironmentError as e:
                    if e.args[0][0] == 'IsolatedWirelessNode':
                        self.process_task_cnt += 1
                        self.logger.append(info_type='task', key=task.task_id, val=(1, ['IsolatedWirelessNode',]))
                        self.logger.log("**IsolatedWirelessNode")
                        raise e

                for link in links_in_path:
                    if isinstance(link, Link):
                        if link.free_bandwidth < task.trans_bit_rate:
                            self.process_task_cnt += 1
                            self.logger.append(info_type='task', key=task.task_id, val=(1, ['NetCongestionError',]))
                            self.logger.log(f"**NetCongestionError: Task {{{task.task_id}}}** network congestion from {{{task.src_name}}} to {{{dst_name}}}")
                            raise EnvironmentError(('NetCongestionError', task.task_id))

                task.trans_time = 0
                for link in links_in_path:
                    task.trans_time += link.base_latency
                task.trans_time += (task.task_size / task.trans_bit_rate) * len(links_in_path)
                
                self.scenario.send_data_flow(task.trans_flow, links_in_path)
                try:
                    self.logger.log(f"Task {{{task.task_id}}}: {{{task.src_name}}} --> {{{dst_name}}}")
                    yield self.controller.timeout(task.trans_time * self.controller.time_scale)
                    task.trans_flow.deallocate()
                    self.logger.log(f"Task {{{task.task_id}}} arrived at Node {{{dst_name}}} in {task.trans_time:.3f}s")
                except simpy.Interrupt:
                    pass
            else:
                task.trans_time = 0

        if not dst.free_cpu_freq > 0:
            try:
                task.allocate(self.now, dst, pre_allocate=True)
                dst.append_task(task)
                self.logger.log(f"Task {{{task.task_id}}} is buffered in Node {{{task.dst_name}}}")
                return
            except EnvironmentError as e:
                self.process_task_cnt += 1
                self.logger.append(info_type='task', key=task.task_id, val=(1, ['InsufficientBufferError',]))
                self.logger.log(e.args[0][1])
                raise e

        if flag_reactive:
            try:
                task.allocate(self.now)
            except EnvironmentError as e:
                self.process_task_cnt += 1
                self.logger.append(info_type='task', key=task.task_id, val=(1, ['TimeoutError',]))
                self.logger.log(e.args[0][1])
                waiting_task = task.dst.pop_task()
                if waiting_task:
                    self.process(task=waiting_task)
                raise e
            self.logger.log(f"Task {{{task.task_id}}} re-activates in Node {{{task.dst_name}}}, waiting {(task.wait_time - task.trans_time):.3f}s")
        else:
            task.allocate(self.now, dst)
        
        self.active_task_dict[task.task_id] = task
        try:
            self.logger.log(f"Processing Task {{{task.task_id}}} in Node {{{task.dst_name}}}")
            yield self.controller.timeout(task.exe_time * self.controller.time_scale)
            self.done_task_collector.put((task.task_id, FLAG_TASK_EXECUTION_DONE, [dst_name, user_defined_info()]))
        except simpy.Interrupt:
            pass

    def monitor_on_done_task_collector(self):
        while True:
            if len(self.done_task_collector.items) > 0:
                while len(self.done_task_collector.items) > 0:
                    task_id, flag, info = self.done_task_collector.get().value
                    self.done_task_info.append((self.controller.now / self.controller.time_scale,
                                                task_id, flag, info))
                    if flag == FLAG_TASK_EXECUTION_DONE:
                        task = self.active_task_dict[task_id]
                        waiting_task = task.dst.pop_task()
                        self.logger.log(f"Task {{{task_id}}} accomplished in Node {{{task.dst_name}}} in {task.exe_time:.3f}s")
                        self.logger.append(info_type='task', key=task.task_id, val=(0, [task.trans_time, task.wait_time, task.exe_time]))
                        task.deallocate()
                        del self.active_task_dict[task_id]
                        self.process_task_cnt += 1
                        if waiting_task:
                            self.process(task=waiting_task)
                    else:
                        raise ValueError("Invalid flag!")
            else:
                self.done_task_info = []
            yield self.controller.timeout(self.refresh_rate * self.controller.time_scale)

    def energy_clock(self, node):
        while True:
            node.energy_consumption += node.idle_energy_coef
            node.energy_consumption += node.exe_energy_coef * ((node.max_cpu_freq - node.free_cpu_freq) ** 3)
            yield self.controller.timeout(self.refresh_rate * self.controller.time_scale)

    def info4frame_clock(self):
        while True:
            self.info4frame[self.controller.now] = {
                'node': {k: item.quantify_cpu_freq() for k, item in self.scenario.get_nodes().items()},
                'edge': {str(k): item.quantify_bandwidth() for k, item in self.scenario.get_links().items()},
            }
            if len(self.config['VisFrame']['TargetNodeList']) > 0:
                self.info4frame[self.controller.now]['target'] = {
                    item: [self.scenario.get_node(item).active_task_ids[:],
                           self.scenario.get_node(item).task_buffer.task_ids[:]]
                    for item in self.config['VisFrame']['TargetNodeList']
                }
            yield self.controller.timeout(self.refresh_rate * self.controller.time_scale)

    @property
    def n_active_tasks(self):
        return len(self.active_task_dict)

    def status(self, node_name: Optional[str] = None, link_args: Optional[Tuple] = None):
        return self.scenario.status(node_name, link_args)
    
    def avg_node_energy(self, node_name_list=None):
        return self.scenario.avg_node_energy(node_name_list) / 1000000
    
    def node_energy(self, node_name):
        return self.scenario.node_energy(node_name) / 1000000

    def close(self):
        for _, node in self.scenario.get_nodes().items():
            self.logger.append(info_type='node', key=node.node_id, val=node.energy_consumption)
        
        if self.config['Basic']['VisFrame'] == "on":
            info4frame_json_object = json.dumps(self.info4frame, indent=4)
            with open(f"{self.config['VisFrame']['LogInfoPath']}/info4frame.json", 'w+') as fw:
                fw.write(info4frame_json_object)

        self.monitor_process.interrupt()
        for p in self.energy_recorders.values():
            if p.is_alive:
                p.interrupt()
        self.energy_recorders.clear()
        if self.config['Basic']['VisFrame'] == "on":
            self.info4frame_recorder.interrupt()

        self.logger.log("Simulation completed!")
