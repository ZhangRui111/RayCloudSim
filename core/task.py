import math
from typing import Optional

from core.infrastructure import Node, Data, DataFlow

__all__ = ["Task"]


class Task:
    """Task that can be placed and executed on a :class:`Node`.

    Attributes:
        task_id: Task ID, unique identifier.
        task_size : Size of the task in bits.
        cycles_per_bit: Number of CPU cycles per bit of task data.
        trans_bit_rate: Transmission bit rate for the task.
        ddl: Maximum tolerable time.

        cpu_freq: CPU frequency during execution (in Hz).
        task_data: Task data object to be processed.
        trans_flow: Data flow object associated with the task.

        trans_time: Time taken for the task to be transmitted.
        wait_time: Time spent waiting for processing on the destination node.
        exe_time: Time spent processing the task on the destination node.

        src_name: Name of the source node that generates the task.
        dst_name: Name of the destination node where the task is executed.
        task_name: Name of the task (for informational purposes).
        exe_cnt: Counter for task execution times.
    """

    def __init__(self, task_id: int, task_size: int, cycles_per_bit: int, trans_bit_rate: int,
                 src_name: str, ddl: Optional[int] = -1, task_name: Optional[str] = ""):
        """Initialize the Task object."""
        self.task_id = task_id
        self.task_size = task_size
        self.cycles_per_bit = cycles_per_bit
        self.trans_bit_rate = trans_bit_rate
        self.ddl = ddl

        self.cpu_freq = -1  # Placeholder for the CPU frequency during execution

        # Task data and flow
        self.task_data = Data(task_size)
        self.trans_flow = DataFlow(trans_bit_rate)

        self.trans_time = -1
        self.wait_time = -1
        self.exe_time = -1

        self.exe_energy = -1  # Placeholder for energy

        self.src_name = src_name
        self.dst = None
        self.dst_id = None
        self.dst_name = None

        self.task_name = task_name
        self.exe_cnt = 0

    def __repr__(self) -> str:
        """Return a string representation of the task."""
        return f"[{self.__class__.__name__}] ({self.task_id})"

    def allocate(self, now: int, node: Optional[Node] = None, pre_allocate: bool = False) -> None:
        """Allocate the task to a node based on the current time."""
        if pre_allocate:
            # Case 1: Buffer task, begin queuing
            self.wait_time = now
            self._pre_allocate_dst(node)
        else:
            if node is None:
                # Case 2: Re-activate task, end queuing
                self.wait_time = (now - self.wait_time) + self.trans_time
                self._post_allocate_dst()
            else:
                # Case 3: Execute task immediately, without queuing
                self.wait_time = self.trans_time
                self._allocate_dst(node)

            # Estimated execution time based on task size and CPU frequency
            self.exe_time = (self.task_size * self.cycles_per_bit) / self.cpu_freq

    def _allocate_dst(self, dst: Node) -> None:
        """Attach the task to the destination node and allocate resources."""
        if self.dst is not None:
            raise ValueError(f"Cannot place {self} on {dst}: It is already placed on {self.dst}.")
        self.dst = dst
        self.dst_id = dst.node_id
        self.dst_name = dst.name
        self.dst.add_task(self)

    def _pre_allocate_dst(self, dst: Node) -> None:
        """Pre-allocate the task to the destination node without resources."""
        if self.dst is not None:
            raise ValueError(f"Cannot place {self} on {dst}: It is already placed on {self.dst}.")
        self.dst = dst
        self.dst_id = dst.node_id
        self.dst_name = dst.name

    def _post_allocate_dst(self) -> None:
        """Allocate resources to the local-waiting task after queuing."""
        self.dst.add_task(self)

    def deallocate(self) -> None:
        """Deallocate the task from the node and free resources."""
        if self.dst is None:
            raise ValueError(f"{self} is not placed on any node.")
        self.dst.remove_task(self)
        self.dst = None
        self.dst_id = None
        self.dst_name = None

        self.exe_cnt += 1
