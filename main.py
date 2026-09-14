import sys
from fly_in import parse_map
from fly_in import find_path
from fly_in import models
from fly_in import display



def main():

    if len(sys.argv) == 1:
        print("Please enter the name of the map file.")
        sys.exit(1)

    map_file = sys.argv[1]

    if not map_file.endswith(".txt"):
        print("Error: map file must be a .txt file.")
        sys.exit(1)

    with open(map_file, "r") as file:
        data = parse_map(file)

    path = find_path(data["graph"], data["graph"].start, data["graph"].end)
    
    if not path:
        print("No path exists between start and end")
        exit(1)
    
    drones = [models.Drone(f"D{i+1}") for i in range(data["nb_drones"])]

    for drone in drones:
        drone.path = path
        
    simulation = models.Simulation(data["graph"], drones)
    # simulation.run()
    
    # for turn_moves in simulation.log:
    #     if turn_moves:
    #         print(" ".join(turn_moves))

    # print(f"\nCompleted in {simulation.turn} turns.")
    while not simulation.all_delivered():
        simulation.run_turn()
        display.print_turn(data["graph"], drones, path, simulation.turn)

    print(f"\nCompleted in {simulation.turn} turns.")

    return data   
if __name__ == "__main__":
    main()
    