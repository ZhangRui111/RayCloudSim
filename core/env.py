import json
import os
import simpy
import networkx as nx

from typing import Optional, Tuple

from core.base_scenario import BaseScenario
from core.infrastructure import Link
from core.task import Task

__all__ = ["EnvLogger", "Env"]


# Flags
FLAG_TASK_EXECUTION_DONE = 0


class EnvLogger:
    def __init__(self, controller):
        self.controller = controller

        self.task_info = {}
        self.node_info = {}

    def log(self, content):
        print("[{:.2f}]: {}".format(self.controller.now, content))

    def append(self, info_type, key, val):
        """Record key information during the simulation.

        Args:
            info_type: 'task' or 'node'
            key: task id or node id
            val: 
                if info_type == 'task': (code: int, info: list)
                    - 0 (success) || [*]
                    - 1 (failure) || [detailed error info,]
                if info_type == 'node':
                    - energy consumption
        """
        assert info_type in ['task', 'node']
        if info_type == 'task':
            self.task_info[key] = val
        else:
            self.node_info[key] = val


class Env:

    def __init__(self, scenario: BaseScenario, config_file):
        # Load the config file
        with open(config_file, 'r') as fr:
            self.config = json.load(fr)
        assert len(self.config['Log']['TargetNodeList']) <= 10, \
            "For aesthetic considerations, the number of tracked nodes is limited to less than 10."
        
        self.scenario = scenario
        self.controller = simpy.Environment()
        self.logger = EnvLogger(self.controller)

        self.active_task_dict = {}  # store current active tasks
        self.done_task_info = []  # catch infos of completed tasks
        self.done_task_collector = simpy.Store(self.controller)
        self.process_task_cnt = 0  # counter

        # self.processed_tasks = []  # for debug

        self.reset()

        # Launch the monitor process
        self.monitor_process = self.controller.process(
            self.monitor_on_done_task_collector())
        
        # Launch all energy recorder processes
        self.energy_recorders = {}
        for _, node in self.scenario.get_nodes().items():
            self.energy_recorders[node.node_id] = self.controller.process(self.energy_clock(node))

        # Launch the info recorder for frames
        if self.config['Basic']['Log'] == "on":
            os.makedirs(self.config['Log']['LogInfoPath'], exist_ok=True)
            os.makedirs(self.config['Log']['LogFramesPath'], exist_ok=True)
            self.info4frame = {}
            self.info4frame_recorder = self.controller.process(self.info4frame_clock())

    @property
    def now(self):
        """The current simulation time."""
        return self.controller.now

    def run(self, until):
        """Run the simulation until the given criterion `until` is met."""
        self.controller.run(until)

    def reset(self):
        """Reset the Env."""
        # Interrupt all activate tasks
        for p in self.active_task_dict.values():
            if p.is_alive:
                p.interrupt()
        self.active_task_dict.clear()

        self.process_task_cnt = 0

        # Reset scenario state
        self.scenario.reset()

        # Clear task monitor info
        self.done_task_collector.items.clear()
        del self.done_task_info[:]

    def process(self, **kwargs):
        """Must be called with keyword args."""
        task_generator = self.execute_task(**kwargs)
        self.controller.process(task_generator)

    def execute_task(self, task: Task, dst_name=None):
        """Transmission and Execution logics.

        dst_name=None means the task is popped from the waiting deque.
        """
        # DuplicateTaskIdError check
        if task.task_id in self.active_task_dict.keys():
            self.process_task_cnt += 1
            self.logger.append(info_type='task', 
                               key=task.task_id, 
                               val=(1, ['DuplicateTaskIdError',]))
            # self.processed_tasks.append(task.task_id)
            log_info = f"**DuplicateTaskIdError: Task {{{task.task_id}}}** " \
                       f"new task (name {{{task.task_name}}}) with a " \
                       f"duplicate task id {{{task.task_id}}}."
            self.logger.log(log_info)
            raise AssertionError(
                ('DuplicateTaskIdError', log_info, task.task_id)
            )

        if dst_name is None:
            flag_reactive = True
        else:
            flag_reactive = False

        if flag_reactive:
            dst = task.dst
        else:
            self.logger.log(f"Task {{{task.task_id}}} generated in "
                            f"Node {{{task.src_name}}}")
            dst = self.scenario.get_node(dst_name)

        if not flag_reactive:
            # Do task transmission, if necessary
            if dst_name != task.src_name:  # task transmission
                try:
                    links_in_path = self.scenario.infrastructure.\
                        get_shortest_links(task.src_name, dst_name)
                # NetworkXNoPathError check
                except nx.exception.NetworkXNoPath:
                    self.process_task_cnt += 1
                    self.logger.append(info_type='task', 
                                       key=task.task_id, 
                                       val=(1, ['NetworkXNoPathError',]))
                    # self.processed_tasks.append(task.task_id)
                    log_info = f"**NetworkXNoPathError: Task " \
                               f"{{{task.task_id}}}** Node {{{dst_name}}} " \
                               f"is inaccessible"
                    self.logger.log(log_info)
                    raise EnvironmentError(
                        ('NetworkXNoPathError', log_info, task.task_id)
                    )
                # IsolatedWirelessNode check
                except EnvironmentError as e:
                    message = e.args[0]
                    if message[0] == 'IsolatedWirelessNode':
                        self.process_task_cnt += 1
                        self.logger.append(info_type='task', 
                                           key=task.task_id, 
                                           val=(1, ['IsolatedWirelessNode',]))
                        # self.processed_tasks.append(task.task_id)
                        log_info = f"**IsolatedWirelessNode"
                        self.logger.log(log_info)
                        raise e

                for link in links_in_path:
                    if isinstance(link, Link):
                        # NetCongestionError check
                        if link.free_bandwidth < task.trans_bit_rate:
                            self.process_task_cnt += 1
                            self.logger.append(info_type='task', 
                                               key=task.task_id, 
                                               val=(1, ['NetCongestionError',]))
                            # self.processed_tasks.append(task.task_id)
                            log_info = f"**NetCongestionError: Task " \
                                       f"{{{task.task_id}}}** network " \
                                       f"congestion Node {{{task.src_name}}} " \
                                       f"--> {{{dst_name}}}"
                            self.logger.log(log_info)
                            raise EnvironmentError(
                                ('NetCongestionError', log_info, task.task_id)
                            )

                task.trans_time = 0
                # ---- Customize the wired/wireless transmission mode here ----
                # wireless transmission:
                if isinstance(links_in_path[0], Tuple):
                    wireless_src_name, wired_dst_name = links_in_path[0]
                    # task.trans_time += func(task, wireless_src_name,
                    #                         wired_dst_name)  # TODO
                    task.trans_time += 0  # (currently only a toy model)
                    links_in_path = links_in_path[1:]
                if isinstance(links_in_path[-1], Tuple):
                    wired_src_name, wireless_dst_name = links_in_path[-1]
                    # task.trans_time += func(task, wired_src_name,
                    #                         wireless_dst_name)  # TODO
                    task.trans_time += 0  # (currently only a toy model)
                    links_in_path = links_in_path[:-1]

                # wired transmission:
                # 0. base latency
                trans_base_latency = 0
                for link in links_in_path:
                    trans_base_latency += link.base_latency
                task.trans_time += trans_base_latency
                # Multi-hop
                task.trans_time += (task.task_size / task.trans_bit_rate) * len(links_in_path)
                # -------------------------------------------------------------

                self.scenario.send_data_flow(task.trans_flow, links_in_path)

                try:
                    self.logger.log(f"Task {{{task.task_id}}}: "
                                    f"{{{task.src_name}}} --> {{{dst_name}}}")
                    yield self.controller.timeout(task.trans_time)
                    task.trans_flow.deallocate()
                    self.logger.log(f"Task {{{task.task_id}}} arrived "
                                    f"Node {{{dst_name}}} with "
                                    f"{{{task.trans_time:.2f}}}s")
                except simpy.Interrupt:
                    pass

        # Task execution
        if not dst.free_cpu_freq > 0:
            # InsufficientBufferError check
            try:
                task.allocate(self.now, dst, pre_allocate=True)
                dst.append_task(task)
                self.logger.log(f"Task {{{task.task_id}}} is buffered in "
                                f"Node {{{task.dst_name}}}")
                return
            except EnvironmentError as e:
                self.process_task_cnt += 1
                self.logger.append(info_type='task', 
                                   key=task.task_id, 
                                   val=(1, ['InsufficientBufferError',]))
                # self.processed_tasks.append(task.task_id)
                self.logger.log(e.args[0][1])
                raise e
            

        # ------------ Customize the execution mode here ------------
        if flag_reactive:
            # TimeoutError check
            try:
                task.allocate(self.now)
            except EnvironmentError as e:  # TimeoutError
                self.process_task_cnt += 1
                self.logger.append(info_type='task', 
                                   key=task.task_id, 
                                   val=(1, ['TimeoutError',]))
                # self.processed_tasks.append(task.task_id)
                self.logger.log(e.args[0][1])

                # Activate a queued task
                waiting_task = task.dst.pop_task()
                if waiting_task:
                    self.process(task=waiting_task)
                
                raise e
            self.logger.log(f"Task {{{task.task_id}}} re-actives in "
                            f"Node {{{task.dst_name}}}")
        else:
            task.allocate(self.now, dst)
        # -----------------------------------------------------------

        # Mark the task as active (i.e., execution status) task
        self.active_task_dict[task.task_id] = task
        try:
            self.logger.log(f"Processing Task {{{task.task_id}}} in"
                            f" {{{task.dst_name}}}")
            yield self.controller.timeout(task.exe_time)
            self.done_task_collector.put((task.task_id,
                                          FLAG_TASK_EXECUTION_DONE,
                                          [dst_name, task.exe_time]))
        except simpy.Interrupt:
            pass

    def monitor_on_done_task_collector(self):
        """Keep watch on the done_task_collector."""
        while True:
            if len(self.done_task_collector.items) > 0:
                while len(self.done_task_collector.items) > 0:
                    task_id, flag, info = self.done_task_collector.get().value
                    self.done_task_info.append((self.now, task_id, flag, info))

                    if flag == FLAG_TASK_EXECUTION_DONE:
                        task = self.active_task_dict[task_id]

                        waiting_task = task.dst.pop_task()

                        self.logger.log(f"Task {{{task_id}}} accomplished in "
                                        f"Node {{{task.dst_name}}} with "
                                        f"{{{task.exe_time:.2f}}}s")
                        self.logger.append(info_type='task', 
                                           key=task.task_id, 
                                           val=(0, [task.trans_time, task.wait_time, task.exe_time]))
                        task.deallocate()
                        del self.active_task_dict[task_id]
                        self.process_task_cnt += 1
                        # self.processed_tasks.append(task.task_id)

                        if waiting_task:
                            self.process(task=waiting_task)

                    else:
                        raise ValueError("Invalid flag!")
            else:
                self.done_task_info = []
                # self.logger.log("")  # turn on: log on every time slot

            yield self.controller.timeout(1)
    
    def energy_clock(self, node):
        """Recorder of node's energy consumption."""
        while True:
            node.energy_consumption += node.idle_energy_coef
            node.energy_consumption += node.exe_energy_coef * (
                node.max_cpu_freq - node.free_cpu_freq) ** 3
            yield self.controller.timeout(1)
    
    def info4frame_clock(self):
        """Recorder the info required for simulation frames."""
        while True:
            self.info4frame[self.now] = {
                'node': {k: item.quantify_cpu_freq() 
                         for k, item in self.scenario.get_nodes().items()},
                'edge': {str(k): item.quantify_bandwidth() 
                         for k, item in self.scenario.get_links().items()},
            }
            if len(self.config['Log']['TargetNodeList']) > 0:
                self.info4frame[self.now]['target'] = {
                    item: [self.scenario.get_node(item).active_task_ids[:], 
                           self.scenario.get_node(item).task_buffer.task_ids[:]]
                    for item in self.config['Log']['TargetNodeList']
                }
            yield self.controller.timeout(1)

    @property
    def n_active_tasks(self):
        """The number of current active tasks."""
        return len(self.active_task_dict)

    def status(self, node_name: Optional[str] = None,
               link_args: Optional[Tuple] = None):
        return self.scenario.status(node_name, link_args)

    def close(self):
        # Record nodes' energy consumption.
        for _, node in self.scenario.get_nodes().items():
            self.logger.append(info_type='node', key=node.node_id, val=node.energy_consumption)
        
        # Save the info4frame
        if self.config['Basic']['Log'] == "on":
            info4frame_json_object = json.dumps(self.info4frame, indent=4)
            with open(f"{self.config['Log']['LogInfoPath']}/info4frame.json", 'w+') as fw:
                fw.write(info4frame_json_object)

        # Terminate activate processes
        self.monitor_process.interrupt()
        for p in self.energy_recorders.values():
            if p.is_alive:
                p.interrupt()
        self.energy_recorders.clear()
        if self.config['Basic']['Log'] == "on":
            self.info4frame_recorder.interrupt()

        self.logger.log("Simulation completed!")
