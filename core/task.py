from typing import Optional

from core.infrastructure import Node, Data, DataFlow

__all__ = ["Task"]


class Task:
    """Task that can be placed and executed on a :class:`Node`.

    Note:
        1. `task_size_exe` and `task_size_trans`

        For example, one image batch can be processed multiple times in the
        destination node while only required one transmission from the source
        node to the destination node.

    Attributes:
        task_id: task id, unique.
        max_cu: maximum CUs requested.
        cu: allocated CUs during execution, cu <= max_cu.

        task_size_exe: task size, measured by unit CU.
        task_data_exe: task data required to be processed by CU.
        real_exe_time: real execution time with allocated CUs.

        task_size_trans: task size, measured by MB.
        task_data_trans: task data required for transmission.
        real_trans_time: real transmission time.

        bit_rate: bit rate of data flow
        trans_flow: data flow, sending the task to the destination node.

        # src: source node that generates the task.
        # src_id: id of the source node.
        src_name: name of the source node.
        dst: destination node that executes the task.
        dst_id: id of the destination node.
        dst_name: name of the destination node.

        task_name: optional
        exe_cnt: execution times counter
    """
    def __init__(self, task_id, max_cu, task_size_exe, task_size_trans,
                 bit_rate, src_name, task_name: Optional[str] = ""):
        self.task_id = task_id
        self.max_cu = max_cu
        self.cu = -1

        self.task_size_exe = task_size_exe
        self.task_data_exe = Data(task_size_exe)
        self.real_exe_time = -1

        self.task_size_trans = task_size_trans
        self.task_data_trans = Data(task_size_trans)
        self.real_trans_time = -1

        self.bit_rate = bit_rate
        self.trans_flow = DataFlow(bit_rate)

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

    def allocate(self, cu=0, node: Node = None):
        if cu <= 0:
            if node is None:
                raise ValueError()
            else:
                self._pre_allocate_dst(node)
        else:
            self._set_cu(cu)
            if node is None:
                self._post_allocate_dst()
            else:
                self._allocate_dst(node)

    def _set_cu(self, cu):
        """Set the real available CUs for execution."""
        self.cu = cu
        self.real_exe_time = self.task_size_exe / self.cu

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
        """Detach the task from the node it is currently placed on and
        deallocate resources."""
        if self.dst is None:
            raise ValueError(f"{self} is not placed on any node.")
        self.dst.remove_task(self)
        self.dst = None
        self.dst_id = None
        self.dst_name = None

        self.cu = -1
        self.real_exe_time = -1
        self.exe_cnt += 1
