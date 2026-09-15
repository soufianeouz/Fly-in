import sys
from fly_in import parser
from fly_in import pathfinding
from fly_in import models
from fly_in import display
from fly_in import simulation
import argparse


def main() -> None:

    if len(sys.argv) == 1:
        print("Please enter the name of the map file.")
        sys.exit(1)
        
    arg = argparse.ArgumentParser()
    arg.add_argument("map_file")
    arg.add_argument("--capacity-info", action="store_true")

    args = arg.parse_args()
    
    map_file = args.map_file
    # capacity = args.capacity_info

    if not map_file.endswith(".txt"):
        print("Error: map file must be a .txt file.")
        sys.exit(1)

    with open(map_file, "r") as file:
        data = parser.parse_map(file)

    path = pathfinding.find_path(
        data["graph"], data["graph"].start, data["graph"].end
    )
    if not path:
        print("No path exists between start and end")
        exit(1)

    drones = [models.Drone(f"D{i+1}") for i in range(data["nb_drones"])]

    for drone in drones:

        drone.path = path

    sim = simulation.Simulation(data["graph"], drones)

    display.print_turn(data["graph"], drones, path, 0)
    while not sim.all_delivered():
        sim.run_turn()
        display.print_turn(data["graph"], drones, path, sim.turn)

    print(f"\nCompleted in {sim.turn} turns.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Keyboard Interrupt!")
