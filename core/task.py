import math

from typing import Optional

from core.infrastructure import Node, Data, DataFlow

__all__ = ["Task"]


class Task:
    """Task that can be placed and executed on a :class:`Node`.

    Attributes:
        task_id: task id, unique.
        task_size: task size in bits.
        cycles_per_bit: amount of CPU cycles per bit of task data.
        trans_bit_rate: bit rate of data flow.
        ddl: maximum tolerable time limit before executing, i.e., trans_time + wait_time <= ddl.

        cpu_freq: obtained cpu frequency during real execution.

        task_data: task data to be processed by CPU.
        trans_flow: data flow, sending the task to the destination node.

        trans_time: time being transmitted from the src node to the dst node.
        wait_time: time waiting to be processed in the dst node.
        exe_time: time being processed in the dst node.

        # src: source node that generates the task.
        # src_id: id of the source node.
        src_name: name of the source node.
        dst: destination node that executes the task.
        dst_id: id of the destination node.
        dst_name: name of the destination node.

        task_name: optional.
        exe_cnt: execution times counter.
    """
    def __init__(self, task_id, task_size, cycles_per_bit, trans_bit_rate, src_name, 
                 ddl: Optional[int] = -1, task_name: Optional[str] = ""):
        self.task_id = task_id
        self.task_size = task_size
        self.cycles_per_bit = cycles_per_bit
        self.trans_bit_rate = trans_bit_rate
        self.ddl = ddl

        self.cpu_freq = -1

        self.task_data = Data(task_size)
        self.trans_flow = DataFlow(trans_bit_rate)

        self.trans_time = -1
        self.wait_time = -1
        self.exe_time = -1

        self.exe_energy = -1  # TODO

        # self.src: Optional[Node] = src
        # self.src_id = self.src.node_id
        # self.src_name = self.src.name
        self.src_name = src_name
        self.dst: Optional[Node] = None
        self.dst_id = None
        self.dst_name = None

        self.task_name = task_name  # only used for info log
        self.exe_cnt = 0

    def __repr__(self):
        return f"[{self.__class__.__name__}] ({self.task_id})"

    def allocate(self, now: int, node: Node=None, pre_allocate: bool=False):
        """Allocate this task to the node.

        Args:
            now: time
            node: dst node
            pre_allocate: if True, pre-allocation and the target node has not allocated resources.
        """
        # Case 1: buffer task, thus, begin queuing
        if pre_allocate:
            self.wait_time = now
            self._pre_allocate_dst(node)
        else:
            # Case 2: re-active task, thus, end queuing
            if node is None:
                # self.wait_time = now - self.wait_time  # trans_time is not involved
                self.wait_time = (now - self.wait_time) + self.trans_time  # trans_time is involved
                # TimeoutError check
                if self.wait_time > self.ddl:
                    raise EnvironmentError(
                        ('TimeoutError', 
                        f"**TimeoutError: Task {{{self.task_id}}}** "
                        f"timeout in Node {{{self.dst.name}}}", self.task_id))
                self._post_allocate_dst()
            # Case 3: execute task immediately, without queuing
            else:
                self.wait_time = 0 + self.trans_time
                self._allocate_dst(node)
            
            # Estimated execution time
            self.exe_time = math.ceil(
                (self.task_size * self.cycles_per_bit) / self.cpu_freq)

    def _allocate_dst(self, dst: Node):
        """Attach the task with the dst node and allocate resources."""
        if self.dst is not None:
            raise ValueError(f"Cannot place {self} on {dst}: "
                             f"It was already placed on {self.dst}.")
        self.dst = dst
        self.dst_id = dst.node_id
        self.dst_name = dst.name
        self.dst.add_task(self)

    def _pre_allocate_dst(self, dst: Node):
        """Attach the task with the dst node."""
        if self.dst is not None:
            raise ValueError(f"Cannot place {self} on {dst}: "
                             f"It was already placed on {self.dst}.")
        self.dst = dst
        self.dst_id = dst.node_id
        self.dst_name = dst.name

    def _post_allocate_dst(self):
        """Allocate resources to the local-waiting task."""
        self.dst.add_task(self)

    def deallocate(self):
        """Detach the task from the node it is currently placed on and deallocate resources."""
        if self.dst is None:
            raise ValueError(f"{self} is not placed on any node.")
        self.dst.remove_task(self)
        self.dst = None
        self.dst_id = None
        self.dst_name = None

        self.exe_cnt += 1
