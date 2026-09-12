import sys
from fly_in import parse_map
from fly_in import find_path



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

    find_path(data["graph"], data["graph"].start, data["graph"].end)
    
    
    return data   
if __name__ == "__main__":
    # print(main())
    main()
    