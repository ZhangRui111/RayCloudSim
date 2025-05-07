from collections import deque, namedtuple
from typing import Optional, List, Dict, Tuple

from core.utils import Location, cal_dis_haversine, cal_dis_euclidean

__all__ = ["Node", "Buffer"]


# Named tuples for buffer and CPU status
BufferStatus = namedtuple("BufferStatus", "free_size, max_size")
CPUStatus = namedtuple("CPUStatus", "free_cpu_freq, max_cpu_freq")


class Node(object):
    """Represents a computing node within the infrastructure graph.

    Nodes can vary in capabilities and represent different types of devices
    or computing resources in a simulated environment.

    Examples of node types:
      - Simple sensors with no processing capabilities.
      - Resource-constrained fog computing nodes.
      - Mobile nodes like cars or smartphones.
      - Data centers with significant computing resources.

    Attributes:
        id (int): The unique identifier for the node.
        name (str): The human-readable name of the node.
        max_cpu_freq (float): The maximum CPU frequency of the node in Hz.
        free_cpu_freq (float): The current available CPU frequency in Hz.
            Note: In the current implementation, this is either 0 (busy) or
            equal to `max_cpu_freq` (idle), supporting one task at a time.
        task_buffer (Buffer): A FIFO buffer for tasks that are waiting to be processed.
            Note: Tasks can be executed directly without being placed in the buffer
            if resources are available.
        location (Optional[Location]): The geographical location of the node.
                                       None if location is not applicable or specified.
        energy_coefficients (Dict[str, float]): A dictionary containing energy consumption
                                                 coefficients for different states.
                                                 Expected keys: 'idle', 'exe'.
        energy_consumption (float): The total energy consumed by the node.
        active_tasks (List[Task]): A list of Task objects currently being processed on the node.
        active_task_ids (List[int]): A list of the IDs of tasks currently being processed.
        total_cpu_freq (float): Accumulator for total CPU frequency used over time (for metrics).
        clock (int): Internal clock or time counter for the node.
    """

    def __init__(self, id: int, name: str, max_cpu_freq: float,
                 max_buffer_size: Optional[int] = 0, location: Optional[Location] = None,
                 energy_coefficients: Optional[Dict[str, float]] = None):
        """Initializes a Node object with specified attributes.

        Args:
            id: The unique node identifier.
            name: The name of the node.
            max_cpu_freq: The maximum CPU frequency in Hz.
            max_buffer_size: The maximum size of the task buffer in bits. Defaults to 0 (no buffer).
            location: The geographical location of the node. Defaults to None.
            energy_coefficients: A dictionary with energy coefficients for 'idle' and 'exe' states.
                                 Defaults to {'idle': 0., 'exe': 0.}.
        """
        # Initialize node attributes
        self.id = id
        self.name = name
        self.max_cpu_freq = max_cpu_freq
        self.free_cpu_freq = max_cpu_freq  # Initially, all CPU frequency is free

        # Initialize task buffer
        self.task_buffer = Buffer(max_buffer_size)

        # Initialize location and energy attributes
        self.location = location
        self.energy_consumption = 0.0  # Total energy consumption, initialized to 0
        # Set default energy coefficients if none are provided
        self.energy_coefficients = energy_coefficients if energy_coefficients is not None else {'idle': 0., 'exe': 0.}

        # Initialize lists to track active tasks
        self.active_tasks: List["Task"] = []
        self.active_task_ids: List[int] = []

        # Initialize metrics accumulators
        self.total_cpu_freq = 0.0
        self.clock = 0

    def __repr__(self):
        return f"{self.name} ({self.free_cpu_freq}/{self.max_cpu_freq})"

    def append_task(self, task: "Task"):
        """Appends a task to the node's task buffer.

        Args:
            task: The Task object to append.
        """
        self.task_buffer.append(task)

    def pop_task(self) -> Optional["Task"]:
        """Removes and returns the first task from the node's task buffer (FIFO).

        Returns:
            The first Task object in the buffer, or None if the buffer is empty.
        """
        return self.task_buffer.pop()

    def _calculate_distance(self, another: "Node", type='euclidean') -> float:
        """Calculates the distance between this node and another node.

        Args:
            another: The other Node object.
            type (str): The type of distance calculation ('euclidean' or 'haversine').
                        Defaults to 'euclidean'.

        Returns:
            The calculated distance as a float.

        Raises:
            ValueError: If an unsupported distance type is provided.
            AttributeError: If location is not defined for one or both nodes when
                            calculating distance.
        """
        if self.location is None or another.location is None:
             raise AttributeError("Location is not defined for one or both nodes.")

        if type == 'haversine':
            return cal_dis_haversine(self.location, another.location)
        elif type == 'euclidean':
            return cal_dis_euclidean(self.location, another.location)
        else:
            raise ValueError(f"Unsupported distance type: {type}")

    def status(self) -> Tuple[CPUStatus, BufferStatus]:
        """Returns the current CPU and buffer status of the node."""
        cpu_status = CPUStatus(self.free_cpu_freq, self.max_cpu_freq)
        buffer_status = self.task_buffer.status()
        return cpu_status, buffer_status

    def cpu_utilization(self) -> float:
        """Returns the ratio of used CPU frequency to the maximum CPU frequency."""
        return (self.max_cpu_freq - self.free_cpu_freq) / self.max_cpu_freq

    def buffer_utilization(self) -> float:
        """Returns the ratio of used buffer size to the maximum buffer size."""
        # Handle case where max_buffer_size is 0 to avoid division by zero
        if self.task_buffer.max_size == 0:
            return 0.0
        return (self.task_buffer.max_size - self.task_buffer.free_size) / self.task_buffer.max_size

    def _add_task(self, task: "Task"):
        """Adds a task to the node's active task list and reserves resources.

        This is an internal method used by the allocation process.

        Args:
            task: The Task object to add.
        """
        self._reserve_resource(task)
        self.active_tasks.append(task)
        self.active_task_ids.append(task.id)

    def _remove_task(self, task: "Task"):
        """Removes a task from the node's active task list and releases resources.

        This is an internal method used by the deallocation process.

        Args:
            task: The Task object to remove.
        """
        self._release_resource(task)
        self.active_tasks.remove(task)
        self.active_task_ids.remove(task.id)

    def _reserve_resource(self, task: "Task"):
        """Reserves CPU resources for the given task.

        In the current implementation, this sets the node's free CPU frequency to 0
        if it was available.

        Args:
            task: The Task object requiring resources.

        Raises:
            ValueError: If there are insufficient CPU resources available.
        """
        if self.free_cpu_freq > 0:
            task.cpu_freq = self.free_cpu_freq  # Assign the node's free CPU freq to the task
            self.free_cpu_freq = 0  # Node is now busy
        else:
            raise ValueError(f"Cannot reserve enough resources on compute node {self}.")

    def _release_resource(self, task: "Task"):
        """Releases CPU resources previously reserved for a task.

        In the current implementation, this sets the node's free CPU frequency back
        to its maximum if it was 0.

        Args:
            task: The Task object releasing resources.

        Raises:
            ValueError: If the node's free CPU frequency is not 0 (unexpected state).
        """
        if self.free_cpu_freq == 0:
            self.free_cpu_freq = self.max_cpu_freq  # Node is now idle
        else:
            raise ValueError(f"Cannot release enough resources on compute node {self}.")

    def reset(self):
        """Resets the node to its initial state.

        This clears the task buffer, active tasks, resets CPU frequency,
        and energy consumption.
        """
        self.free_cpu_freq = self.max_cpu_freq
        self.energy_consumption = 0.0
        self.task_buffer.reset()
        self.active_tasks.clear()
        self.active_task_ids.clear()

        self.total_cpu_freq = 0.0
        self.clock = 0


class Buffer(object):
    """Represents a FIFO (First-In, First-Out) buffer for managing tasks.

    This buffer is used by nodes to queue tasks when they cannot be processed
    immediately.

    Attributes:
        max_size (int): The maximum capacity of the buffer in bits.
        free_size (int): The current available space in the buffer in bits.
        buffer (deque): A deque (double-ended queue) storing the buffered Task objects.
        task_ids (List[int]): A list of the IDs of the tasks currently in the buffer.
    """

    def __init__(self, max_size: int):
        """Initializes a Buffer object with a specified maximum size."""
        self.max_size = max_size
        self.free_size = max_size

        self.buffer = deque()  # FIFO queue of buffered Task objects
        self.task_ids: List[int] = []  # List of buffered task IDs

    def append(self, task: "Task"):
        """Appends a task to the buffer if enough space is available.

        Args:
            task: The Task object to append to the buffer.

        Raises:
            EnvironmentError: If there is insufficient buffer space for the task.
        """
        if task.task_size <= self.free_size:
            self.free_size -= task.task_size
            self.task_ids.append(task.id)
            self.buffer.append(task)
        else:
            # Raise a custom error indicating insufficient buffer space
            raise EnvironmentError(
                ('InsufficientBufferError',
                 f"**InsufficientBufferError: Task {{{task.id}}}** "
                 f"insufficient buffer in Node {{{task.dst.name}}}", task.id))

    def pop(self) -> Optional["Task"]:
        """Removes and returns the first task from the buffer (FIFO).

        Returns:
            The first Task object in the buffer, or None if the buffer is empty.
        """
        if self.buffer:
            task = self.buffer.popleft()
            self.task_ids.remove(task.id)
            self.free_size += task.task_size
            return task
        return None # Return None explicitly if buffer is empty

    def status(self) -> BufferStatus:
        """Returns the current buffer utilization status."""
        return BufferStatus(self.free_size, self.max_size)

    def reset(self):
        """Resets the buffer to its initial state, clearing all tasks and freeing space."""
        self.free_size = self.max_size
        self.buffer.clear()
        self.task_ids.clear()
