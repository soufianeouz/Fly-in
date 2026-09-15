import sys
from . import models

ZONES_KEY = ["start_hub", "hub", "end_hub"]


def parse_nb_drones(line):
    nb_drones = int(line[len("nb_drones:"):].strip())
    if nb_drones <= 0:
        print("Error: nb_drones must be a positive integer.")
        sys.exit(1)
    return nb_drones


def extract_metadata(value):
    if "[" in value:

        if value.count("[") != 1:
            print("Error: invalid metadata format")
            sys.exit(1)

        if "]" not in value:
            print("Error: missing ']' in metadata")
            sys.exit(1)

        data, metadata = value.split("[", 1)

        if metadata.count("]") != 1 or not metadata.rstrip().endswith("]"):
            print("Error: invalid metadata format")
            sys.exit(1)

        metadata = metadata.rstrip("]").strip()

        meta_parts = metadata.split()
    else:
        data = value
        meta_parts = []

    data = data.strip()
    return data, meta_parts


def parse_zone(key, data, meta_parts, dup_start_check, dup_end_check):
    if key == "start_hub":
        dup_start_check += 1
        if dup_start_check > 1:
            print("Error: duplicate start_hub")
            sys.exit(1)
    elif key == "end_hub":
        dup_end_check += 1
        if dup_end_check > 1:
            print("Error: duplicate end_hub")
            sys.exit(1)
    elif key == "hub":
        pass
    else:
        print("invalid zones keys words!")
        sys.exit(1)

    parts_zone = data.split()
    if len(parts_zone) != 3:
        print("Error: invalid zone format")
        sys.exit(1)

    if "-" in parts_zone[0]:

        print("Error: zone name cannot contain '-'")
        sys.exit(1)

    zone_name = parts_zone[0]
    x = int(parts_zone[1])
    y = int(parts_zone[2])

    color = None
    max_drones = 1
    zone_type = models.ZoneType.NORMAL

    seen_metadata = set()
    for meta in meta_parts:
        if "=" not in meta:
            print(f"Error: invalid metadata '{meta}'")
            sys.exit(1)
        meta_key, meta_value = meta.split("=", 1)
        if meta_key in seen_metadata:
            print(f"Error: duplicate metadata '{meta_key}'")
            sys.exit(1)
        seen_metadata.add(meta_key)
        if meta_key == "color":
            color = meta_value
        elif meta_key == "max_drones":
            max_drones = int(meta_value)
            if max_drones <= 0:
                print("Error: max_drones must be positive")
                sys.exit(1)
        elif meta_key == "zone":
            try:
                zone_type = models.ZoneType(meta_value)
            except ValueError:

                print(f"Error: invalid zone type '{meta_value}'")
                sys.exit(1)
        else:
            print("Error: unknown metadata")
            sys.exit(1)
    # if zone == "st/
    zone = models.Zone(
        name=zone_name,
        x=x,
        y=y,
        zone_type=zone_type,
        color=color,
        max_drones=max_drones
    )

    return zone_name, zone, dup_start_check, dup_end_check


def parse_connection(data, meta_parts, zones, connections_seen):
    if data.count("-") != 1:
        print("Error: invalid connection format")
        sys.exit(1)

    zone1, zone2 = data.split("-", 1)
    zone1 = zone1.strip()
    zone2 = zone2.strip()
    if zone1 not in zones:
        print(f"Error: zone '{zone1}' is not defined")
        sys.exit(1)
    if zone2 not in zones:
        print(f"Error: zone '{zone2}' is not defined")
        sys.exit(1)

    if zone1 == zone2:
        print("Error: a zone cannot connect to itself")
        sys.exit(1)

    connection_pair = frozenset((zone1, zone2))

    if connection_pair in connections_seen:
        print("Error: duplicate connection")
        sys.exit(1)

    connections_seen.add(connection_pair)

    max_link_capacity = 1

    if len(meta_parts) > 1:
        print("Error: connection must have at most one metadata parameter")
        sys.exit(1)

    if len(meta_parts) == 1:
        if meta_parts[0].count("=") != 1:
            print("Error: invalid connection metadata")
            sys.exit(1)

        meta_key, meta_value = meta_parts[0].split("=")

        if meta_key != "max_link_capacity":
            print("Error: unknown connection metadata")
            sys.exit(1)

        max_link_capacity = int(meta_value)

        if max_link_capacity <= 0:

            print("Error: max_link_capacity must be positive")
            sys.exit(1)

    connection = models.Connection(
        zone_a=zone1,
        zone_b=zone2,
        max_link_capacity=max_link_capacity
    )
    return connection


def parse_map(map_file):

    try:
        flage = 0
        zones = {}

        connections = []
        connections_seen = set()

        dup_start_check = 0
        dup_end_check = 0
        nb_drones = None

        for line in map_file:
            if line.strip() == "" or line.strip()[0] == "#":
                continue

            line = line.split("#", 1)[0].strip()
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()

            if key == "nb_drones":
                if flage == 1:
                    print("Error: duplicate nb_drones")
                    sys.exit(1)
                nb_drones = parse_nb_drones(line)
                flage = 1
                continue
            elif flage == 0:
                print("The firstline must define the numberof drones!")
                sys.exit(1)

            data, meta_parts = extract_metadata(value)

            if key in ZONES_KEY and flage == 1:
                zone_name, zone, dup_start_check, dup_end_check = parse_zone(
                    key, data, meta_parts, dup_start_check, dup_end_check
                )
                if key == "start_hub":
                    start_name = zone_name
                    zone.max_drones = nb_drones

                elif key == "end_hub":
                    end_name = zone_name
                    zone.max_drones = nb_drones

                if zone_name in zones:
                    print(f"Error: duplicate zone name '{zone_name}'")
                    sys.exit(1)
                zones[zone_name] = zone

            elif key == "connection" and flage == 1:
                connection = parse_connection(
                    data, meta_parts, zones, connections_seen

                )
                connections.append(connection)
            else:
                print(f"Error: unknown key '{key}'")
                sys.exit(1)

        if dup_start_check != 1:
            print("Error: exactly one start_hub is required")
            sys.exit(1)
        if dup_end_check != 1:
            print("Error: exactly one end_hub is required")
            sys.exit(1)

    except FileNotFoundError:
        print(f"Error: file '{map_file}' does not exist.")
        sys.exit(1)

    except ValueError:
        print("Error: invalid values input!")
        sys.exit(1)

    graph = models.Graph(
        zones=zones, connections=connections, start=start_name, end=end_name
    )

    return {"nb_drones": nb_drones, "graph": graph}
