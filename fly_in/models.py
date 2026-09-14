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
    
    def name(self) -> str:
        """Return the display name of this connection, e.g. 'a-b'."""
        return f"{self.zone_a}-{self.zone_b}"


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

    def get_neighbors(self, zone_name: str) -> list[str]:
        """Return all connections touching the given zone."""

        neighbors = []

        for connection in self.connections:
            if connection.zone_a == zone_name:
                neighbors.append(connection.zone_b)
            elif connection.zone_b == zone_name:
                neighbors.append(connection.zone_a)
        
        return neighbors
            
            

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
        self.in_transit = False
        self.transit_turns_left = 0

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

    def run(self) -> None:
        """Run turns until every drone has been delivered."""
        while not self.all_delivered():
            self.run_turn()

    def run_turn(self) -> None:
        """Advance the simulation by a single turn."""
        self.turn += 1
        moves: list[str] = []

        for drone in self.drones:
            if drone.delivered:
                continue

            if drone.in_transit:
                move = self._advance_transit(drone)
            else:
                move = self._try_start_move(drone)

            if move is not None:
                moves.append(move)

        self.log.append(moves)

    def _get_connection(self, zone_a: str, zone_b: str) -> Connection | None:
        """Find the connection linking two zone names, if one exists."""
        for connection in self.graph.connections:
            if {connection.zone_a, connection.zone_b} == {zone_a, zone_b}:
                return connection
        return None

    def _try_start_move(self, drone: Drone) -> str | None:
        next_name = drone.next_zone()
        if next_name is None:
            return None

        current_name = drone.current_zone()
        next_zone = self.graph.zones[next_name]
        connection = self._get_connection(current_name, next_name)

        if connection is not None and not connection.has_space():
            return None

        if next_name != self.graph.end and not next_zone.has_space():
            return None

        if next_zone.zone_type == ZoneType.RESTRICTED:
            drone.in_transit = True
            drone.transit_turns_left = 1
            connection.users.add(drone.id)
            return f"{drone.id}-{connection.name()}"

        self._commit_arrival(drone, current_name, next_name, connection)
        return f"{drone.id}-{next_name}"

    def _advance_transit(self, drone: Drone) -> str | None:
        """Advance a drone that is mid-transit toward a restricted zone.

        Returns:
            The log entry string once the drone arrives, None otherwise.
        """
        drone.transit_turns_left -= 1
        if drone.transit_turns_left > 0:
            return None  # still in flight, no log entry this turn

        current_name = drone.current_zone()
        next_name = drone.next_zone()
        if next_name is None:
            return None

        connection = self._get_connection(current_name, next_name)
        drone.in_transit = False
        self._commit_arrival(drone, current_name, next_name, connection)
        return f"{drone.id}-{next_name}"

    def _commit_arrival(
        self,
        drone: Drone,
        current_name: str,
        next_name: str,
        connection: Connection | None,
    ) -> None:
        """Move a drone into its next zone and update occupancy state."""
        current_zone = self.graph.zones[current_name]
        next_zone = self.graph.zones[next_name]

        current_zone.occupants.discard(drone.id)
        next_zone.occupants.add(drone.id)

        if connection is not None:
            connection.users.discard(drone.id)

        drone.move_to_next()