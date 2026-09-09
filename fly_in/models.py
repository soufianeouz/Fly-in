"""Data models for the Fly-in drone routing simulation."""

from enum import Enum


class ZoneType(Enum):
    """Possible zone types, as defined in the map format."""

    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class Zone:
    """A single zone (node) in the network."""

    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        zone_type: ZoneType,
        color: str | None = None,
        max_drones: int | float = 1,
    ) -> None:
        """Create a zone.

        Args:
            name: Unique name of the zone.
            x: X coordinate.
            y: Y coordinate.
            zone_type: Type of the zone (normal, blocked, restricted, priority).
            color: Optional color tag for display.
            max_drones: Max number of drones allowed at the same time.
        """
        self.name = name
        self.x = x
        self.y = y
        self.zone_type = zone_type
        self.color = color
        self.max_drones = max_drones
        self.occupants: set[str] = set()

    def has_space(self) -> bool:
        """Return True if the zone can accept another drone."""
        return len(self.occupants) < self.max_drones


class Connection:
    """A bidirectional connection between two zones."""

    def __init__(
        self,
        zone_a: str,
        zone_b: str,
        max_link_capacity: int = 1,
    ) -> None:
        """Create a connection between two zone names.

        Args:
            zone_a: Name of the first zone.
            zone_b: Name of the second zone.
            max_link_capacity: Max number of drones allowed on this
                connection at the same time.
        """
        self.zone_a = zone_a
        self.zone_b = zone_b
        self.max_link_capacity = max_link_capacity
        self.users: set[str] = set()

    def has_space(self) -> bool:
        """Return True if the connection can accept another drone."""
        return len(self.users) < self.max_link_capacity

    def other_end(self, zone_name: str) -> str:
        """Return the name of the zone on the other side of this connection."""
        if zone_name == self.zone_a:
            return self.zone_b
        return self.zone_a


class Graph:
    """The full network of zones and connections."""

    def __init__(
        self,
        zones: dict[str, Zone],
        connections: list[Connection],
        start: str,
        end: str,
    ) -> None:
        """Create the graph.

        Args:
            zones: Mapping of zone name to Zone.
            connections: List of connections.
            start: Name of the start zone.
            end: Name of the end zone.
        """
        self.zones = zones
        self.connections = connections
        self.start = start
        self.end = end

    def neighbors(self, zone_name: str) -> list[Connection]:
        """Return all connections touching the given zone."""
        return [
            c for c in self.connections
            if c.zone_a == zone_name or c.zone_b == zone_name
        ]


class Drone:
    """A single drone moving from start to end."""

    def __init__(self, drone_id: str) -> None:
        """Create a drone with no path assigned yet.

        Args:
            drone_id: Unique identifier of the drone (e.g. "D1").
        """
        self.id = drone_id
        self.path: list[str] = []
        self.position = 0
        self.delivered = False

    def current_zone(self) -> str:
        """Return the name of the zone the drone is currently in."""
        return self.path[self.position]

    def next_zone(self) -> str | None:
        """Return the name of the next zone on the path, or None if none left."""
        if self.position + 1 >= len(self.path):
            return None
        return self.path[self.position + 1]

    def move_to_next(self) -> None:
        """Advance the drone to the next zone on its path."""
        self.position += 1
        if self.current_zone() == self.path[-1]:
            self.delivered = True


class Simulation:
    """Runs the turn-by-turn simulation of all drones."""

    def __init__(self, graph: Graph, drones: list[Drone]) -> None:
        """Create the simulation.

        Args:
            graph: The network of zones and connections.
            drones: The drones to simulate.
        """
        self.graph = graph
        self.drones = drones
        self.turn = 0
        self.log: list[list[str]] = []

    def all_delivered(self) -> bool:
        """Return True if every drone has reached the end zone."""
        return all(d.delivered for d in self.drones)

    def run_turn(self) -> None:
        """Advance the simulation by one turn (logic to be filled in)."""
        self.turn += 1