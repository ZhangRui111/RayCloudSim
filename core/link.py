from typing import Optional, List

from core.node import Node
from core.utils import DataFlow, cal_dis_haversine, cal_dis_euclidean

__all__ = ["Link"]


class Link(object):
    """Represents an unidirectional network link connecting two nodes in the infrastructure graph.

    Attributes:
        src (Node): The source node of the link.
        dst (Node): The destination node of the link.
        max_bandwidth (float): The maximum bandwidth of the link in bits per second (bps).
        free_bandwidth (float): The current available bandwidth of the link in bps.
        dis (float): The distance between the source and destination nodes.
        base_latency (float): The base latency of the link, useful for routing policies.
        data_flows (List[DataFlow]): A list of DataFlow objects currently allocated on this link.
    """

    def __init__(self, src: Node, dst: Node, max_bandwidth: float, base_latency: Optional[float] = 0):
        """Initializes a Link object with specified attributes.

        Args:
            src: The source Node object.
            dst: The destination Node object.
            max_bandwidth: The maximum bandwidth in bps.
            base_latency: The base latency of the link. Defaults to 0.
        """
        self.src = src
        self.dst = dst
        self.max_bandwidth = max_bandwidth
        self.base_latency = base_latency
        try:
            # Calculate distance between source and destination nodes
            self.dis = self._calculate_distance()
        except AttributeError:
            # Default distance if location is not available
            self.dis = 1
        self.free_bandwidth = max_bandwidth  # Initially, all bandwidth is free
        self.data_flows: List[DataFlow] = []  # List to track allocated data flows

    def __repr__(self):
        return (
            f"{self.src.name} --> {self.dst.name} "
            f"({self.free_bandwidth}/{self.max_bandwidth}) "
            f"({self.base_latency})"
        )

    def _calculate_distance(self, type='euclidean') -> float:
        """Calculate and return the distance between the source and destination nodes.

        Args:
            type (str): The type of distance calculation ('euclidean' or 'haversine').
                        Defaults to 'euclidean'.

        Returns:
            The calculated distance as a float.

        Raises:
            ValueError: If an unsupported distance type is provided.
            AttributeError: If location is not defined for one or both nodes.
        """
        if self.src.location is None or self.dst.location is None:
             raise AttributeError("Location is not defined for one or both nodes.")

        if type == 'haversine':
            return cal_dis_haversine(self.src.location, self.dst.location)
        elif type == 'euclidean':
            return cal_dis_euclidean(self.src.location, self.dst.location)
        else:
            raise ValueError(f"Unsupported distance type: {type}")

    def _add_data_flow(self, data_flow: DataFlow):
        """Adds a data flow to the link and reserves bandwidth.

        This is an internal method used by the DataFlow allocation process.

        Args:
            data_flow: The DataFlow object to add.
        """
        self._reserve_bandwidth(data_flow.bit_rate)
        self.data_flows.append(data_flow)

    def _remove_data_flow(self, data_flow: DataFlow):
        """Removes a data flow from the link and releases bandwidth.

        This is an internal method used by the DataFlow deallocation process.

        Args:
            data_flow: The DataFlow object to remove.
        """
        self._release_bandwidth(data_flow.bit_rate)
        self.data_flows.remove(data_flow)

    def _reserve_bandwidth(self, bandwidth: float):
        """Reserves bandwidth for a data flow on this link.

        Args:
            bandwidth: The amount of bandwidth to reserve in bps.

        Raises:
            ValueError: If there is insufficient free bandwidth available.
        """
        if self.free_bandwidth < bandwidth:
            raise ValueError(f"Cannot reserve {bandwidth} bandwidth on link {self}. Not enough free bandwidth.")
        
        self.free_bandwidth -= bandwidth

    def _release_bandwidth(self, bandwidth: float):
        """Releases bandwidth previously reserved for a data flow on this link.

        Args:
            bandwidth: The amount of bandwidth to release in bps.

        Raises:
            ValueError: If releasing the bandwidth would exceed the maximum bandwidth.
        """
        if self.free_bandwidth + bandwidth > self.max_bandwidth:
            raise ValueError(f"Cannot release {bandwidth} bandwidth on link {self}. Exceeds max bandwidth.")
        
        self.free_bandwidth += bandwidth
    
    def bandwidth_utilization(self) -> float:
        """Returns the ratio of used bandwidth to the maximum bandwidth."""
        # Handle case where max_bandwidth is 0 to avoid division by zero
        if self.max_bandwidth == 0:
            return 0.0
        return (self.max_bandwidth - self.free_bandwidth) / self.max_bandwidth

    def reset(self):
        """Resets the link's bandwidth to its maximum and clears the data flows."""
        self.free_bandwidth = self.max_bandwidth
        self.data_flows.clear()
