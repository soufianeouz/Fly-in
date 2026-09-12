from . import models


def find_path(graph: models.Graph, start: str, end: str) -> list[str]:
    distances = {}
    previous = {}

    for zone_name in graph.zones:
        distances[zone_name] = float("inf")
        previous[zone_name] = None

    distances[start] = 0

    unvisited = set(graph.zones)

    while unvisited:
        current = None
        smallest_distance = float("inf")

        for zone_name in unvisited:
            if distances[zone_name] < smallest_distance:
                smallest_distance = distances[zone_name]
                current = zone_name

        if current is None:
            break

        unvisited.remove(current)

        if current == end:
            break

        for neighbor in graph.get_neighbors(current):

            if graph.zones[neighbor].zone_type == models.ZoneType.BLOCKED:
                continue

            if graph.zones[neighbor].zone_type == models.ZoneType.RESTRICTED:
                movement_cost = 2
            else:
                movement_cost = 1

            new_distance = distances[current] + movement_cost

            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous[neighbor] = current

    if distances[end] == float("inf"):
        return []

    path = []
    current = end

    while current is not None:
        path.append(current)
        current = previous[current]

    path.reverse()

    return path