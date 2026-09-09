import sys
import models



try:
    if len(sys.argv) == 1:
        print("Please enter the name of the map file.")
        sys.exit(1)
    map_file = sys.argv[1]
    
    if not map_file.endswith(".txt"):
        print("Error: map file must be a .txt file.")
        sys.exit(1)
    flage = 0
    zones_key = ["start_hub", "hub", "end_hub"]
    dup_start_check = 0
    dup_end_check = 0
    with open(map_file, "r") as file:
        for line in file:
            if line.strip() == "" or line.strip()[0] == "#":
                continue
            
            line = line.split("#", 1)[0].strip()
            if line[:len("nb_drones:")] == "nb_drones:":
                nb_drones = int(line[len("nb_drones:"):].strip())
                if nb_drones <= 0:
                    print("Error: nb_drones must be a positive integer.")
                    sys.exit(1)
                flage = 1
                continue
            elif flage == 0:
                print("The firstline must define the numberof drones!")
                sys.exit(1)
            
            point = line[:line.index(":")]
            if point in zones_key and flage == 1:
                if point.strip() == "start_hub":
                    dup_start_check += 1
                    if dup_start_check > 1:
                        print("Error: duplicate start_hub")
                        sys.exit(1)
                    # zones_key.remove("start_hub")
                    print(point.strip())
                elif point.strip()  == "end_hub":
                    dup_end_check += 1
                    if dup_end_check > 1:
                        print("Error: duplicate end_hub")
                        sys.exit(1)
                    # zones_key.remove("end_hub")
                    print(point.strip())
                elif point.strip()  == "hub":
                    print(point.strip())
                else:
                    print("invalid zones keys words!")
                    sys.exit(1) 
            else:
                print("invalid order of the data!")
                sys.exit(1)



except FileNotFoundError:
    print(f"Error: file '{map_file}' does not exist.")
    sys.exit(1)

except ValueError:
    print("Error: invalid nb_drones value")
    sys.exit(1)

