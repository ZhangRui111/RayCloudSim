import simpy
import networkx as nx

from typing import Optional, Tuple

from core.base_scenario import BaseScenario
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
        """Reset the scenario."""
        # Interrupt all activate tasks
        for p in self.active_task_dict.values():
            if p.is_alive:
                p.interrupt()
        self.active_task_dict.clear()
        # Reset scenario state
        self.scenario.reset()
        # Clear task monitor info
        self.done_task_collector.items.clear()
        del self.done_task_info[:]

    def process(self, **kwargs):
        """Must be called with keyword args."""
        task_generator = self.execute_task(**kwargs)
        self.controller.process(task_generator)

    def execute_task(self, task: Task, dst_name):
        """Transmission and Execution logics."""

        self.logger.log(f"Task {{{task.task_id}}} generated in "
                        f"Node {{{task.src_name}}}")

        dst = self.scenario.get_node(dst_name)

        # DuplicateTaskIdError check
        if task.task_id in self.active_task_dict.keys():
            raise AssertionError(
                ('DuplicateTaskIdError',
                 f"**DuplicateTaskIdError: Task {{{task.task_id}}}** "
                 f"new task (name {{{task.task_name}}}) with a duplicate "
                 f"task id {{{task.task_id}}}.", task.task_id)
            )

        # Do task transmission, if necessary
        if dst_name != task.src_name:  # task transmission
            try:
                links_in_path = self.scenario.infrastructure.get_shortest_links(
                    task.src_name, dst_name)
            except nx.exception.NetworkXNoPath:
                raise EnvironmentError(
                    ('NetworkXNoPathError',
                     f"**NetworkXNoPathError: Task {{{task.task_id}}}** "
                     f"Node {{{dst_name}}} is inaccessible", task.task_id)
                )

            for link in links_in_path:
                if link.bandwidth - link.used_bandwidth < task.bit_rate:
                    raise EnvironmentError(
                        ('NetCongestionError',
                         f"**NetCongestionError: Task {{{task.task_id}}}** "
                         f"network congestion Node {{{task.src_name}}} --> "
                         f"{{{dst_name}}}", task.task_id)
                    )

            # * 8: MB --> Mbps
            task.real_trans_time = task.task_size_trans * 8 / task.bit_rate
            self.scenario.send_data_flow(task.trans_flow, links_in_path)
            self.active_task_dict[task.task_id] = task
            try:
                yield self.controller.timeout(task.real_trans_time)
                self.done_task_collector.put((task.task_id, 0,
                                              [dst_name, task.real_trans_time]))
            except simpy.Interrupt:
                pass
        else:  # local execution
            self.active_task_dict[task.task_id] = task

        # Task execution
        free_cus = dst.cu - dst.used_cu
        if free_cus <= 0:
            self.done_task_collector.put((task.task_id, 2, [dst_name]))
            raise EnvironmentError(
                ('NoFreeCUsError',
                 f"**NoFreeCUsError: Task {{{task.task_id}}}** "
                 f"insufficient CUs in Node {{{dst_name}}}", task.task_id)
            )
        task.allocate(min(free_cus, task.max_cu), dst)
        try:
            yield self.controller.timeout(task.real_exe_time)
            self.done_task_collector.put((task.task_id, 1,
                                          [dst_name, task.real_exe_time]))
        except simpy.Interrupt:
            pass

    def monitor_on_done_task_collector(self):
        """Keep watch on the done_task_collector."""
        while True:
            if len(self.done_task_collector.items) > 0:
                while len(self.done_task_collector.items) > 0:
                    task_id, flag, info = self.done_task_collector.get().value
                    self.done_task_info.append(
                        (self.now, task_id, flag, info))
                    task = self.active_task_dict[task_id]
                    if flag == 0:
                        task.trans_flow.deallocate()
                        self.logger.log(f"Task {{{task_id}}} arrived "
                                        f"Node {{{info[0]}}} with "
                                        f"{{{info[1]:.2f}}}s")
                    elif flag == 1:
                        task.deallocate()
                        self.logger.log(f"Task {{{task_id}}} accomplished in "
                                        f"Node {{{info[0]}}} with "
                                        f"{{{info[1]:.2f}}}s")
                        del self.active_task_dict[task_id]
                    elif flag == 2:  # arrived dst node but find no CUs
                        del self.active_task_dict[task_id]
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
