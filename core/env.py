import simpy
import networkx as nx

from typing import Optional, Tuple

from core.base_scenario import BaseScenario
from core.infrastructure import Link
from core.flag import *
from core.task import Task
from core.visualization import plot_2d_network_graph

__all__ = ["EnvLogger", "Env"]


class EnvLogger:
    def __init__(self, controller):
        self.controller = controller

    def log(self, content):
        print("[{:.2f}]: {}".format(self.controller.now, content))


class Env:

    def __init__(self, scenario: BaseScenario):
        # Main components
        self.scenario = scenario
        self.controller = simpy.Environment()
        self.logger = EnvLogger(self.controller)

        self.active_task_dict = {}  # store current active tasks
        self.done_task_info = []  # catch infos of completed tasks
        self.done_task_collector = simpy.Store(self.controller)
        self.process_task_cnt = 0  # counter

        self.reset()

        # Launch the monitor process
        self.monitor_process = self.controller.process(
            self.monitor_on_done_task_collector())

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
            self.logger.log(f"Task {{{task.task_id}}} re-actives in "
                            f"Node {{{task.dst_name}}}")
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
                except nx.exception.NetworkXNoPath:
                    self.process_task_cnt += 1
                    log_info = f"**NetworkXNoPathError: Task " \
                               f"{{{task.task_id}}}** Node {{{dst_name}}} " \
                               f"is inaccessible"
                    self.logger.log(log_info)
                    raise EnvironmentError(
                        ('NetworkXNoPathError', log_info, task.task_id)
                    )

                for link in links_in_path:
                    if isinstance(link, Link):
                        if link.bandwidth - link.used_bandwidth < task.bit_rate:
                            self.process_task_cnt += 1
                            log_info = f"**NetCongestionError: Task " \
                                       f"{{{task.task_id}}}** network " \
                                       f"congestion Node {{{task.src_name}}} " \
                                       f"--> {{{dst_name}}}"
                            self.logger.log(log_info)
                            raise EnvironmentError(
                                ('NetCongestionError', log_info, task.task_id)
                            )

                task.real_trans_time = 0
                # ---- Customize the wired/wireless transmission mode here ----
                # wireless transmission:
                if isinstance(links_in_path[0], tuple):
                    wireless_src_name, wired_dst_name = links_in_path[0]
                    # task.real_trans_time += func(task, wireless_src_name,
                    #                              wired_dst_name)  # TODO
                    task.real_trans_time += 0  # (currently only a toy model)
                    links_in_path = links_in_path[1:]
                if isinstance(links_in_path[-1], tuple):
                    wired_src_name, wireless_dst_name = links_in_path[-1]
                    # task.real_trans_time += func(task, wired_src_name,
                    #                              wireless_dst_name)  # TODO
                    task.real_trans_time += 0  # (currently only a toy model)
                    links_in_path = links_in_path[:-1]

                # wired transmission:
                # 0. base latency
                trans_base_latency = 0
                for link in links_in_path:
                    trans_base_latency += link.base_latency
                task.real_trans_time += trans_base_latency
                # 1. MB --> Mbps
                # 2. Multi-hop
                task.real_trans_time += (task.task_size_trans * 8
                                         / task.bit_rate) * len(links_in_path)
                # -------------------------------------------------------------

                self.scenario.send_data_flow(task.trans_flow, links_in_path)

                try:
                    self.logger.log(f"Task {{{task.task_id}}}: "
                                    f"{{{task.src_name}}} --> {{{dst_name}}}")
                    yield self.controller.timeout(task.real_trans_time)
                    task.trans_flow.deallocate()
                    self.logger.log(f"Task {{{task.task_id}}} arrived "
                                    f"Node {{{dst_name}}} with "
                                    f"{{{task.real_trans_time:.2f}}}s")
                except simpy.Interrupt:
                    pass

        # Task execution
        free_cus = dst.cu - dst.used_cu
        if free_cus <= 0:
            if dst.buffer_size > 0:
                try:
                    dst.buffer_append_task(task)
                    task.allocate(0, dst)
                    self.logger.log(f"Task {{{task.task_id}}} is buffered in "
                                    f"Node {{{task.dst_name}}}")
                    return
                except EnvironmentError as e:  # InsufficientBufferError
                    self.process_task_cnt += 1
                    self.logger.log(e.args[0][1])
                    raise e
            else:
                self.process_task_cnt += 1
                log_info = f"**NoFreeCUsError: Task {{{task.task_id}}}** " \
                           f"no free CUs in Node {{{dst_name}}}"
                self.logger.log(log_info)
                raise EnvironmentError(
                    ('NoFreeCUsError', log_info, task.task_id)
                )

        # ------------ Customize the execution mode here ------------
        if flag_reactive:
            task.allocate(min(free_cus, task.max_cu))
        else:
            task.allocate(min(free_cus, task.max_cu), dst)
        # -----------------------------------------------------------

        # Mark the task as active (i.e., execution status) task
        self.active_task_dict[task.task_id] = task
        try:
            self.logger.log(f"Processing Task {{{task.task_id}}} in"
                            f" {{{task.dst_name}}}")
            yield self.controller.timeout(task.real_exe_time)
            self.done_task_collector.put((task.task_id,
                                          FLAG_TASK_EXECUTION_DONE,
                                          [dst_name, task.real_exe_time]))
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

                        waiting_task = task.dst.buffer_pop_task()

                        self.logger.log(f"Task {{{task_id}}} accomplished in "
                                        f"Node {{{task.dst_name}}} with "
                                        f"{{{task.real_exe_time:.2f}}}s")
                        task.deallocate()
                        del self.active_task_dict[task_id]
                        self.process_task_cnt += 1

                        if waiting_task:
                            self.process(task=waiting_task)

                    # elif flag == FLAG_TASK_TRANSMISSION_DONE:
                    #     task = self.active_task_dict[task_id]
                    #     task.trans_flow.deallocate()
                    #     self.logger.log(f"Task {{{task_id}}} arrived "
                    #                     f"Node {{{info[0]}}} with "
                    #                     f"{{{info[1]:.2f}}}s")
                    #     # del self.active_task_dict[task_id]
                    #
                    # elif flag == FLAG_TASK_ARRIVE_NO_CUS:
                    #     # del self.active_task_dict[task_id]
                    #     pass
                    #
                    # elif flag == FLAG_TASK_ARRIVE_NO_BUFFER:
                    #     # del self.active_task_dict[task_id]
                    #     pass

                    else:
                        raise ValueError("Invalid flag!")
            else:
                self.done_task_info = []
                # self.logger.log("")  # turn on: log on every time slot

            yield self.controller.timeout(1)

    @property
    def n_active_tasks(self):
        """The number of current active tasks."""
        return len(self.active_task_dict)

    def vis_graph(self, save_as):
        """Visualize the graph/network."""
        plot_2d_network_graph(self.scenario.infrastructure.graph,
                              save_as=save_as)

    def status(self, node_name: Optional[str] = None,
               link_args: Optional[Tuple] = None):
        return self.scenario.status(node_name, link_args)

    def close(self):
        self.logger.log("Simulation completed!")
        self.monitor_process.interrupt()
