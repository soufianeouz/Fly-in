"""Colored terminal visualization for the Fly-in simulation."""

from fly_in.models import Drone, Graph, Zone

ANSI_COLORS: dict[str, str] = {
    "green": "\033[92m",
    "red": "\033[91m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "gray": "\033[90m",
    "cyan": "\033[96m",
    "magenta": "\033[95m",
}
DEFAULT_COLOR = "\033[97m"  # white, used for unknown/missing colors
RESET = "\033[0m"


def colorize(text: str, color: str | None) -> str:
    """Wrap text in an ANSI color code based on the zone's color name.

    Args:
        text: The text to colorize.
        color: The zone's color name (e.g. "red"), or None.

    Returns:
        The text wrapped in ANSI codes, resetting color afterward.
    """
    code = ANSI_COLORS.get(color, DEFAULT_COLOR)
    return f"{code}{text}{RESET}"


def format_zone(zone: Zone, drones: list[Drone]) -> str:
    occupants = []

    for drone in drones:
        if drone.current_zone() == zone.name:
            occupants.append(drone.id)
    nb = len(occupants)
    occupants = ", ".join(occupants)

    return f"{colorize(zone.name, zone.color)} [{occupants}]"

def print_turn(
    graph: Graph, drones: list[Drone], path: list[str], turn: int
) -> None:
    """Print one turn's state as a colored chain of zones.

    Args:
        graph: The network of zones.
        drones: All drones in the simulation.
        path: The ordered list of zone names to display (start to end).
        turn: The current turn number.
    """
    if turn == 0:
        print("Initial state:")
    else:
        print(f"Turn {turn}")

    blocks = []

    for name in path:
        zone = graph.zones[name]
        block = format_zone(zone, drones)
        blocks.append(block)

    print(" -> ".join(blocks))
