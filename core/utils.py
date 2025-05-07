import math

from typing import Optional, List


__all__ = ["Location", "Data", "DataFlow"]


def cal_dis_haversine(loc1: "Location", loc2: "Location") -> float:
    """
    Calculate the Haversine distance (great-circle distance) between two points on Earth.

    Args:
        loc1: The first Location object.
        loc2: The second Location object.

    Returns:
        The distance between the two locations in meters.
    """
    # Convert decimal degrees to radians.
    lat1, lon1, lat2, lon2 = map(math.radians, [loc1.x, loc1.y, loc2.x, loc2.y])

    # Compute differences.
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Haversine formula.
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Radius of Earth in kilometers (6371000 for meters)
    R = 6371000
    distance = R * c
    return distance


def cal_dis_euclidean(loc1: "Location", loc2: "Location") -> float:
    """Calculate the Euclidean distance between two points in a 2D plane.

    Args:
        loc1: The first Location object.
        loc2: The second Location object.

    Returns:
        The Euclidean distance between the two locations.
    """
    distance = math.sqrt(
        (loc1.x - loc2.x) ** 2 +
        (loc1.y - loc2.y) ** 2
    )
    return distance


class Location:
    """Represents a 2D geographical location with x and y coordinates.

    This class is used to define the position of nodes in the infrastructure.

    Attributes:
        x (float): The x-coordinate.
        y (float): The y-coordinate.
    """

    def __init__(self, x: float, y: float):
        """Initializes a Location object with specified coordinates."""
        self.x = x
        self.y = y

    def __repr__(self):
        return f"({self.x}, {self.y})"

    def __eq__(self, another):
        if not isinstance(another, Location):
            return NotImplemented
        return self.x == another.x and self.y == another.y

    def __hash__(self):
        return hash((self.x, self.y))

    def loc(self):
        """Returns the coordinates as a tuple (x, y)."""
        return self.x, self.y


class Data(object):
    """Represents a block of data with a specified size."""

    def __init__(self, data_size: int):
        """Initializes a Data object with a specified data size.

        Args:
            data_size: The size of the data in bits.
        """
        self.data_size = data_size

    def __repr__(self):
        return f"[{self.__class__.__name__}] ({self.data_size})"


class DataFlow(object):
    """Represents a flow of data through a sequence of network links.

    This class is used to model the transmission of data between nodes.

    Attributes:
        bit_rate (int): The bit rate of the data flow in bits per second (bps).
        links (Optional[List[Link]]): The list of Link objects representing the path
                                      the data flow is allocated to. None if not allocated.
    """

    def __init__(self, bit_rate: int):
        """Initializes a DataFlow object with a specified bit rate.

        Args:
            bit_rate: The bit rate of the data flow in bps.
        """
        self.bit_rate = bit_rate
        self.links: Optional[List["Link"]] = None

    def __repr__(self):
        return f"[{self.__class__.__name__}] ({self.bit_rate})"

    def allocate(self, links: List["Link"]):
        """Allocates the data flow to a list of links.

        This method assigns the data flow to a specific path of links and
        reserves the required bandwidth on each link.

        Args:
            links: A list of Link objects representing the path for the data flow.

        Raises:
            ValueError: If the data flow is already allocated to a path.
        """
        if self.links is not None:
            raise ValueError(f"Cannot place {self} on {links}: It is already placed on path {self.links}.")

        self.links = links
        for link in self.links:
            link._add_data_flow(self)

    def deallocate(self):
        """Deallocates the data flow from its assigned links.

        This method releases the reserved bandwidth on each link in the path.

        Raises:
            ValueError: If the data flow is not currently allocated to any links.
        """
        if self.links is None:
            raise ValueError(f"{self} is not placed on any links.")
        
        for link in self.links:
            link._remove_data_flow(self)
        self.links = None
