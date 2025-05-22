from typing import Optional

from core.utils import Data, DataFlow
from core.node import Node

__all__ = ["Task"]


class Task:
    """Task that can be placed and executed on a :class:`Node`.

    Attributes:
        id: Task ID, unique identifier.
        task_size : Size of the task in bits.
        cycles_per_bit: Number of CPU cycles per bit of task data.
        trans_bit_rate: Transmission bit rate for the task.
        ddl: Maximum tolerable time (deadline).

        cpu_freq: CPU frequency during execution (in Hz).
        task_data: Task data object to be processed.
        trans_flow: Data flow object associated with the task transmission.

        trans_time: Time taken for the task to be transmitted.
        wait_time: Time spent waiting for processing on the destination node.
        exe_time: Time spent processing the task on the destination node.
        exe_energy: Energy consumed during task execution.

        src_name: Name of the source node that generates the task.
        dst: The destination Node object where the task is executed.
        dst_id: ID of the destination node.
        dst_name: Name of the destination node.
        task_name: Name of the task (for informational purposes).
        exe_cnt: Counter for task execution times.
    """

    def __init__(self, id: int, task_size: int, cycles_per_bit: int, trans_bit_rate: int,
                 src_name: str, ddl: Optional[int] = -1, task_name: Optional[str] = ""):
        """Initialize the Task object.

        Args:
            id: Unique identifier for the task.
            task_size: Size of the task in bits.
            cycles_per_bit: Number of CPU cycles required per bit of task data.
            trans_bit_rate: Transmission bit rate for sending the task.
            src_name: Name of the source node generating the task.
            ddl: Optional maximum tolerable time (deadline) for task completion. Defaults to -1 (no deadline).
            task_name: Optional name for the task (for informational purposes). Defaults to "".
        """
        self.id = id
        self.task_size = task_size
        self.cycles_per_bit = cycles_per_bit
        self.trans_bit_rate = trans_bit_rate
        self.ddl = ddl

        self.cpu_freq = -1  # Placeholder for the CPU frequency during execution

        # Initialize task data and transmission flow objects
        self.task_data = Data(task_size)
        self.trans_flow = DataFlow(trans_bit_rate)

        # Initialize time and energy metrics
        self.trans_time = -1
        self.wait_time = -1
        self.exe_time = -1
        self.exe_energy = -1  # Placeholder for energy consumed during execution

        # Initialize node information
        self.src_name = src_name
        self.dst: Optional[Node] = None  # Destination node object
        self.dst_id: Optional[int] = None  # Destination node ID
        self.dst_name: Optional[str] = None  # Destination node name

        self.task_name = task_name
        self.exe_cnt = 0

    def __repr__(self) -> str:
        return f"[{self.__class__.__name__}] ({self.id})"

    def allocate(self, now: int, node: Optional[Node] = None, pre_allocate: bool = False) -> None:
        """Allocate the task to a node.

        Args:
            now: The current simulation time.
            node: The destination node for allocation (if not pre-allocated).
            pre_allocate: If True, pre-allocate the task to a node without immediately allocating resources.
                          If False, allocate the task and its resources.
        """
        if pre_allocate:
            # Case 1: Pre-allocate task to a node (e.g., for buffering/queuing)
            self.wait_time = now  # Record the time when queuing begins
            self._pre_allocate_dst(node)
        else:
            if node is None:
                # Case 2: Re-activate a previously pre-allocated task, ending its queuing time
                self.wait_time = (now - self.wait_time) + self.trans_time  # Calculate total wait time
                self._post_allocate_dst()
            else:
                # Case 3: Allocate and execute task immediately without prior queuing
                self.wait_time = self.trans_time  # Wait time is just transmission time
                self._allocate_dst(node)

            # Estimated execution time based on task size and CPU frequency
            self.exe_time = (self.task_size * self.cycles_per_bit) / self.cpu_freq

    def _allocate_dst(self, dst: Node) -> None:
        """Attach the task to the destination node and allocate resources for immediate execution."""
        if self.dst is not None:
            raise ValueError(f"Cannot place {self} on {dst}: It is already placed on {self.dst}.")
        self.dst = dst
        self.dst_id = dst.id
        self.dst_name = dst.name
        self.dst._add_task(self)  # Add task to the node's task list

    def _pre_allocate_dst(self, dst: Node) -> None:
        """Pre-allocate the task to the destination node without immediately allocating resources.
        Used for tasks that will be queued or buffered on the node.
        """
        if self.dst is not None:
            raise ValueError(f"Cannot place {self} on {dst}: It is already placed on {self.dst}.")
        self.dst = dst
        self.dst_id = dst.id
        self.dst_name = dst.name

    def _post_allocate_dst(self) -> None:
        """Allocate resources to a previously pre-allocated (local-waiting) task after it finishes queuing."""
        self.dst._add_task(self)  # Add task to the node's task list

    def deallocate(self) -> None:
        """Deallocate the task from the node and free resources."""
        if self.dst is None:
            raise ValueError(f"{self} is not placed on any node.")
        self.dst._remove_task(self)  # Remove task from the node's task list
        self.dst = None
        self.dst_id = None
        self.dst_name = None

        self.exe_cnt += 1
