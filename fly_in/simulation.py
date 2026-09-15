from . import models


class Simulation:
    """Runs the turn-by-turn simulation of all drones."""

    def __init__(
        self, graph: models.Graph, drones: list[models.Drone]
    ) -> None:
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

        for drone in self.drones:
            if drone.delivered:
                continue

            if drone.in_transit:
                self._advance_transit(drone)
            else:
                self._try_start_move(drone)

    def _get_connection(
        self, zone_a: str, zone_b: str
    ) -> models.Connection | None:
        """Find the connection linking two zone names, if one exists."""
        for connection in self.graph.connections:
            if {connection.zone_a, connection.zone_b} == {zone_a, zone_b}:
                return connection
        return None

    def _try_start_move(self, drone: models.Drone) -> None:
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

        if next_zone.zone_type == models.ZoneType.RESTRICTED:
            drone.in_transit = True
            drone.transit_turns_left = 1
            connection.users.add(drone.id)
            return

        self._commit_arrival(drone, current_name, next_name, connection)
        return

    def _advance_transit(self, drone: models.Drone) -> None:
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
        return

    def _commit_arrival(
        self,
        drone: models.Drone,
        current_name: str,
        next_name: str,
        connection: models.Connection | None,
    ) -> None:
        """Move a drone into its next zone and update occupancy state."""
        current_zone = self.graph.zones[current_name]
        next_zone = self.graph.zones[next_name]

        current_zone.occupants.discard(drone.id)
        next_zone.occupants.add(drone.id)

        if connection is not None:
            connection.users.discard(drone.id)

        drone.move_to_next()
