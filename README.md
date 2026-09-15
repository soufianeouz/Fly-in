*This project has been created as part of the 42 curriculum by <login1>.*

# Fly-in

## Description

Fly-in is a drone routing and scheduling simulator. Given a map of zones connected
by paths, and a number of drones starting at a shared base, the program computes an
efficient route from the start zone to the end zone and then simulates all drones
moving through the network turn by turn, respecting zone capacity, connection
capacity, and special movement rules for restricted zones.

The goal of the simulation is to deliver every drone from the start zone to the end
zone in as few simulation turns as possible, while never violating occupancy or
capacity constraints.

The project is split into four responsibilities:
- **Parsing** the map file format into structured objects.
- **Pathfinding** (Dijkstra's algorithm) to compute the lowest-cost route through
  the network.
- **Simulation/scheduling**, which moves drones turn by turn along that route while
  respecting all capacity and timing constraints.
- **Visualization**, which prints a colored, turn-by-turn view of the network state.

## Instructions

### Requirements
- Python 3.10 or later
- No external dependencies are required to run the simulation itself. `flake8`,
  `mypy`, and `pytest` are used for development/quality checks only.

### Installation
```bash
make install
```
This creates a virtual environment (if not already present) and installs the
development dependencies (flake8, mypy, pytest).

### Running the simulation
```bash
make run MAP=maps/easy_1.txt
```
or directly:
```bash
python3 main.py maps/easy_1.txt
```

### Debugging
```bash
make debug MAP=maps/easy_1.txt
```
Runs the program under Python's built-in `pdb` debugger.

### Linting and type checking
```bash
make lint          # flake8 + mypy with the mandated flags
make lint-strict    # flake8 + mypy --strict
```

### Cleaning
```bash
make clean
```
Removes `__pycache__`, `.mypy_cache`, and the virtual environment.

### Running tests
```bash
make test
```
Runs the (non-graded) test suite in `tests/`, covering parser edge cases,
pathfinding correctness, and scheduler behavior.

## Algorithm Choices

### Pathfinding: Dijkstra's algorithm
Each zone has a movement cost based on its type: `normal` and `priority` zones cost
1 turn to enter, `restricted` zones cost 2 turns, and `blocked` zones can never be
entered. Since the graph has only positive edge weights and the goal is to find the
lowest-total-cost route, Dijkstra's algorithm is the natural fit — it is implemented
from scratch in `pathfinding.py`, with no external graph libraries, as required.
Blocked zones are simply never relaxed as neighbors, effectively removing them from
the search space.

BFS was not used because it assumes uniform edge cost and would incorrectly treat a
path through several `normal` zones as worse than a shorter path through a single,
more expensive `restricted` zone. DFS was not used because it does not guarantee an
optimal (lowest-cost) path at all — it simply explores the graph depth-first.

### Scheduling: custom turn-based greedy scheduler
Dijkstra only computes a static route; it has no notion of time, other drones, or
capacity. The actual movement of drones is handled by a custom scheduler
(`Simulation.run_turn()`), which processes every drone once per turn:

1. A drone that is mid-transit toward a restricted zone simply advances its
   remaining transit counter; it cannot wait or change its mind mid-flight.
2. Otherwise, the drone attempts to move to the next zone on its path. The move is
   only committed if the destination zone has available capacity (`max_drones`) and,
   if applicable, the connecting link has available capacity (`max_link_capacity`).
   The end zone is always treated as having unlimited capacity, regardless of its
   metadata, per the subject's rules.
3. If a drone cannot move, it waits — this is a valid outcome, not an error — and is
   simply omitted from that turn's movement log.
4. Moving into a `restricted` zone takes exactly two turns: the drone is marked
   in-transit on the connection for one turn, then arrives unconditionally on the
   next turn, with no possibility of waiting mid-transit, matching the subject's
   rule exactly.

This scheduler is not a named textbook algorithm; it is bespoke logic built to
satisfy this project's specific occupancy and timing rules. It is a simple,
deterministic, fixed-order greedy approach: it processes drones in a stable order
each turn and only commits moves that are currently legal. This keeps the logic easy
to reason about, test, and explain, at the cost of not always finding the
theoretically fastest possible schedule on heavily congested maps — an acceptable
trade-off given the project's time constraints and the fact that turn-count targets
in the subject are described as approximate benchmarks, not hard requirements.

### Complexity
- Dijkstra: O(V^2) in the current implementation (a simple "pick smallest unvisited"
  loop rather than a heap-based priority queue), since the graphs involved in this
  project are small enough that this has no practical performance impact.
- Each simulation turn: O(D × E) in the worst case, where D is the number of active
  drones and E is the number of connections (used when looking up a connection
  between two zone names). Again, negligible at this project's scale.
- Paths are computed once per run and reused by all drones sharing the same route;
  they are not recomputed on every turn.

## Visual Representation

After every turn (including an initial "Turn 0" showing the starting state before
any movement), the program prints the full chain of zones on the drones' path, in
order, each zone name colored according to its `color` metadata from the map file,
followed by the list of drone IDs currently occupying that zone:

```
Turn 0
start [D1, D2, D3, D4] -> junction [ ] -> path_a [ ] -> goal [ ]
Turn 1
start [D3, D4] -> junction [D1, D2] -> path_a [ ] -> goal [ ]
...
Turn 6
start [ ] -> junction [ ] -> path_a [ ] -> goal [D1, D2, D3, D4]
```

Zone names are rendered using ANSI color codes matching their declared `color`
(e.g. green, red, yellow, blue, gray), so at a glance it is possible to see both the
type of each zone (by its color) and exactly which drones occupy it, turn by turn.
Delivered drones remain visible accumulating at the end zone rather than
disappearing, so the full delivery progress stays visible throughout the run. This
was chosen over a full graphical interface because it is fast to build, requires no
extra dependencies, and is fully sufficient to satisfy the requirement of showing
both zone state and drone movement clearly.

## Example Input and Output

Input (`maps/linear_path.txt`):
```
nb_drones: 2
start_hub: start 0 0 [color=green]
hub: waypoint1 1 0 [color=red]
hub: waypoint2 2 0 [color=red]
end_hub: end 3 0 [color=yellow]
connection: start-waypoint1
connection: waypoint1-waypoint2
connection: waypoint2-end
```

Output:
```
Turn 0
start [D1, D2] -> waypoint1 [ ] -> waypoint2 [ ] -> end [ ]
Turn 1
start [D2] -> waypoint1 [D1] -> waypoint2 [ ] -> end [ ]
Turn 2
start [ ] -> waypoint1 [D2] -> waypoint2 [D1] -> end [ ]
Turn 3
start [ ] -> waypoint1 [ ] -> waypoint2 [D2] -> end [D1]
Turn 4
start [ ] -> waypoint1 [ ] -> waypoint2 [ ] -> end [D1, D2]

Completed in 4 turns.
```

The two drones are staggered by one turn because each intermediate zone has a
default capacity of 1, so the second drone must wait until the first has moved on.

## Resources

- [Dijkstra's algorithm — overview and correctness](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- Python `typing` module documentation, for type hints used throughout the project
- `mypy` and `flake8` documentation, for the static analysis and style checks
  required by the project
- ANSI escape code reference, for the colored terminal output in `display.py`

### AI usage disclosure
AI assistance (Claude) was used throughout this project as a design and code-review
partner, not as a black-box code generator. Specifically, it was used to:
- Talk through ambiguous parsing rules (e.g. how to interpret "the first line must
  define nb_drones" in the presence of comments/blank lines, how to handle
  duplicate or malformed metadata keys) and decide on a defensible interpretation.
- Compare pathfinding algorithm choices (Dijkstra vs. BFS/DFS) and justify why
  Dijkstra fits this problem's weighted-cost requirements.
- Review draft code (`models.py`, the scheduler in particular) for bugs — it
  identified a deadlock caused by the end zone incorrectly enforcing a capacity
  limit, which was then fixed and verified.
- Discuss the OOP structure and file layout of the project.

Every function in the codebase was written, tested, and is understood well enough
to explain and modify live, per the project's evaluation requirements. AI-suggested
code was never copy-pasted without being reviewed and run against real test maps
first.