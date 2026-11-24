*This project has been created as part of the 42 curriculum by nuakmurz .*

# Fly-in — Multi-Drone Routing Simulator

## Overview

| Property | Details |
|---|---|
| Language | Python 3.10+ |
| Architecture | Object-Oriented Programming |
| Pathfinding | Dijkstra's Algorithm |
| Simulation | Discrete Turn-Based Simulation |
| Optimization | Multi-Path Routing and Movement Scheduling |
| Code Quality Tools | Flake8, Mypy |
| Mandatory Maps Completed | 9/9 |
| Optimal Mandatory Results | 7/9 |
| Challenger Map | Completed in 51 turns |

## Description

Fly-in is a graph-based multi-drone routing and simulation system developed as part of the 42 Common Core curriculum.

The objective is to navigate multiple drones from a starting hub to a destination hub through a network of interconnected zones while minimizing the total number of simulation turns.

The system must coordinate simultaneous drone movements, respect zone and connection capacities, handle restricted areas, and prevent movement conflicts.

Unlike a traditional shortest-path problem, Fly-in requires the coordination of multiple independent agents competing for shared network resources. Finding the shortest path for a single drone does not necessarily produce the best result for the entire fleet.

The project combines graph theory, pathfinding algorithms, resource management, heuristic optimization, and discrete-event simulation.

## Features

- Object-oriented architecture.
- Custom weighted graph implementation.
- Dijkstra-based shortest-path algorithm.
- Alternative route discovery.
- Multi-path drone distribution.
- Round-robin route assignment.
- Turn-based simulation engine.
- Simultaneous drone movements.
- Zone and connection capacity management.
- Restricted zone traversal.
- Movement conflict resolution.
- Strategic waiting.
- Map parsing and input validation.
- Colored terminal visualization.
- Unreachable destination detection.
- Error handling.
- Python type annotations.
- Automated code quality checks.
- No external graph-processing libraries.

## Instructions

### Requirements

- Python 3.10 or later
- Make
- Flake8
- Mypy

### Installation

Install the project dependencies:

```bash
make install
```

### Running the Simulation

Execute the simulation with a map file:

```bash
python3 main.py path/to/map.txt
```

Alternatively, use the Makefile:

```bash
make run MAP=path/to/map.txt
```

### Debugging

```bash
make debug
```

### Code Quality

Run Flake8 and Mypy:

```bash
make lint
```

### Cleaning

Remove generated files and Python caches:

```bash
make clean
```

## Project Architecture

The project follows an object-oriented design, separating graph representation, input parsing, pathfinding, drone management, and simulation logic.

### Architectural Overview

```text
                 Input Map
                     |
                     v
              Parsing Layer
                     |
                     v
                   Graph
                 /       \
             Zones     Connections
                     |
                     v
             Pathfinding System
                     |
                     v
              Route Distribution
                     |
                     v
               Simulation Engine
                     |
                     v
              Terminal Output
```

### Main Components

| Component | Responsibility |
|---|---|
| Parser | Reads and validates map files. |
| Graph | Represents the network topology and connections. |
| Zone | Stores zone properties, movement costs, and occupancy limits. |
| Drone | Stores individual drone positions, paths, and movement states. |
| Pathfinding | Calculates shortest and alternative routes. |
| Route Distribution | Assigns available routes to drones. |
| Simulation | Coordinates movements and manages simulation turns. |
| Visualization | Displays drone movements and simulation progress. |

### Design Principles

- Separation of concerns.
- Encapsulation.
- Modular architecture.
- Explicit state management.
- Reusable components.
- Type safety.
- Maintainability.

## Graph Representation

The environment is represented as a weighted, bidirectional graph:

```text
G = (V, E)
```

Where:

- V represents the set of zones.
- E represents the set of connections between zones.

Each zone contains information about its type, coordinates, movement cost, and maximum occupancy.

Each connection defines a possible movement between two zones and has its own traversal capacity.

### Zone Types

| Zone Type | Movement Cost | Behavior |
|---|---:|---|
| Normal | 1 turn | Standard movement |
| Priority | 1 turn | Preferred during pathfinding |
| Restricted | 2 turns | Requires multi-turn traversal |
| Blocked | Inaccessible | Cannot be entered |

### Capacity Constraints

Two types of capacity constraints are considered:

- **Zone capacity:** Maximum number of drones that can occupy a zone simultaneously.
- **Connection capacity:** Maximum number of drones that can traverse a connection simultaneously.

The starting and destination hubs have unlimited occupancy.

## Algorithm and Implementation Strategy

### 1. Dijkstra's Algorithm

Dijkstra's algorithm is used as the foundation of the pathfinding system.

The algorithm calculates shortest paths in a graph with non-negative movement costs.

Initially, the starting zone has a distance of zero, while all other zones have an infinite distance.

During each iteration, neighboring zones are evaluated using the relaxation formula:

```text
new_distance = distance[current] + movement_cost
```

If the newly calculated distance is smaller than the previously recorded distance, the distance and predecessor information are updated.

```text
distance[neighbor] = min(
    distance[neighbor],
    distance[current] + movement_cost
)
```

The predecessor information allows the pathfinding system to reconstruct the route from the destination back to the starting zone.

Dijkstra's algorithm was selected because movement costs are non-negative and may differ depending on the destination zone type.

### 2. Alternative Route Discovery

Using only a single shortest path can create congestion when multiple drones attempt to traverse the same zones and connections.

The routing system therefore searches for alternative paths.

```text
                 Zone A
               /        \
Start --------            -------- Goal
               \        /
                 Zone B
```

Alternative routes allow drones to use different parts of the network, potentially increasing overall throughput and reducing waiting time.

### 3. Drone Distribution

Available routes are assigned to drones using a round-robin distribution strategy.

For example, given three available routes and six drones:

| Drone | Assigned Route |
|---|---|
| D1 | Route 1 |
| D2 | Route 2 |
| D3 | Route 3 |
| D4 | Route 1 |
| D5 | Route 2 |
| D6 | Route 3 |

This strategy distributes drones across multiple routes instead of concentrating all traffic on a single path.

However, an equal distribution does not necessarily produce the optimal result when routes have different lengths or capacities.

### 4. Turn-Based Simulation

The simulation operates in discrete turns.

During each turn, drones may:

- Move to an adjacent zone.
- Begin crossing a connection toward a restricted zone.
- Complete a restricted-zone traversal.
- Remain in their current position when movement is unavailable.

The simulation continues until every drone reaches the destination hub.

### 5. Movement Scheduling

The simulation engine coordinates drone movements while maintaining a consistent network state.

The movement scheduling process considers:

```text
Start of Turn
      |
      v
Evaluate Drone States
      |
      v
Determine Possible Movements
      |
      v
Check Zone and Connection Capacities
      |
      v
Resolve Movement Conflicts
      |
      v
Apply Validated Movements
      |
      v
Update Simulation State
      |
      v
Check Completion
```

Movements are coordinated so that multiple drones can advance during the same simulation turn without violating capacity constraints.

### 6. Resource and Capacity Management

Zones and connections are treated as shared resources.

When a drone leaves a zone, the released capacity can become available to another drone during the same turn.

For example:

```text
Before movement:

Start -> [D2] -> [D1] -> Goal

After simultaneous movement:

Start -> [  ] -> [D2] -> Goal(D1)
```

This behavior allows drones to advance through the network without introducing unnecessary waiting turns.

### 7. Restricted Zone Handling

Entering a restricted zone requires two simulation turns.

```text
Turn 1: Drone enters the connection.
Turn 2: Drone arrives at the restricted zone.
```

During traversal, the drone occupies the connection.

The drone must arrive at the destination zone on the following turn and cannot remain indefinitely on the connection.

The simulation must therefore consider both connection availability and destination capacity when scheduling restricted movements.

### 8. Optimization Strategy

The primary optimization objective is to minimize the total number of turns required to deliver all drones.

This objective is also known as minimizing the makespan.

```text
T = max(arrival_time(D1), ..., arrival_time(Dn))
```

The implementation combines:

- Shortest-path discovery.
- Alternative route generation.
- Round-robin drone distribution.
- Capacity-aware movement scheduling.
- Simultaneous movements.
- Strategic waiting.

The implemented approach is heuristic. It aims to produce efficient and valid solutions without guaranteeing a globally optimal solution for every possible graph topology.

## Complexity Analysis

Let:

- V be the number of zones.
- E be the number of connections.
- D be the number of drones.
- T be the number of simulation turns.

The graph requires approximately O(V + E) space when represented using adjacency lists.

The complexity of Dijkstra's algorithm depends on the data structure used to select the next zone.

| Dijkstra Implementation | Time Complexity |
|---|---|
| Linear minimum selection | O(V² + E) |
| Binary heap priority queue | O((V + E) log V) |

The overall simulation cost also depends on:

- The number of discovered routes.
- The number of drones.
- The number of simulation turns.
- Capacity validation.
- Movement conflict resolution.

The exact end-to-end complexity depends on the routing and scheduling implementation.

## Input Format

The program accepts a map describing the number of drones, available zones, connections, and optional metadata.

### Example Input

```text
nb_drones: 2

start_hub: start 0 0 [color=green]
hub: middle 1 0 [color=blue]
end_hub: goal 2 0 [color=yellow]

connection: start-middle
connection: middle-goal
```

### Supported Metadata

| Metadata | Description |
|---|---|
| zone | Defines the zone type. |
| color | Defines the visualization color. |
| max_drones | Defines maximum zone occupancy. |
| max_link_capacity | Defines maximum connection occupancy. |

### Input Validation

The parser is designed to validate:

- Drone count.
- Starting and destination hubs.
- Unique zone names.
- Integer coordinates.
- Valid zone types.
- Positive capacity values.
- Existing connection endpoints.
- Duplicate connections.
- Metadata syntax.
- Reachability of the destination.

Invalid inputs are reported through error messages rather than allowing uncontrolled execution.

## Example Output

```text
D1-middle
D1-goal D2-middle
D2-goal
```

Each line represents one simulation turn.

In this example, both drones reach the destination in three turns while respecting the default capacity constraints.

Drones that remain stationary are omitted from the movement output.

## Visual Representation

The simulation provides colored terminal output to visualize drone movements and distinguish zones.

Zone colors are derived from the metadata defined in the input map.

The terminal visualization helps users:

- Follow individual drone movements.
- Observe simultaneous movements.
- Identify occupied zones.
- Understand restricted-zone traversal.
- Identify congestion and waiting behavior.
- Debug routing and scheduling decisions.

The visualization provides a readable representation of the simulation without requiring a graphical interface.

## Performance Benchmarks

The implementation was tested against all nine mandatory maps and the optional Challenger map.

Reference optimal values are taken from version 2.0 of the Fly-in subject.

### Easy Maps

| Map | Drones | Optimal Turns | Result | Status |
|---|---:|---:|---:|---|
| Linear Path | 2 | 4 | 4 | Optimal |
| Simple Fork | 4 | 4 | 4 | Optimal |
| Basic Capacity | 4 | 4 | 4 | Optimal |

### Medium Maps

| Map | Drones | Optimal Turns | Result | Status |
|---|---:|---:|---:|---|
| Dead End Trap | 5 | 8 | 8 | Optimal |
| Circular Loop | 6 | 10 | 10 | Optimal |
| Priority Puzzle | 5 | 6 | 7 | Completed |

### Hard Maps

| Map | Drones | Optimal Turns | Result | Status |
|---|---:|---:|---:|---|
| Maze Nightmare | 8 | 13 | 13 | Optimal |
| Capacity Hell | 12 | 16 | 16 | Optimal |
| Ultimate Challenge | 15 | 26 | 27 | Completed |

### Challenger Map

| Map | Drones | Optimal Turns | Result | Status |
|---|---:|---:|---:|---|
| The Impossible Dream | 25 | 43 | 51 | Completed |

### Benchmark Summary

| Metric | Result |
|---|---:|
| Mandatory Maps Completed | 9/9 |
| Mandatory Completion Rate | 100% |
| Optimal Mandatory Maps | 7/9 |
| Optimal Solution Rate | 77.78% |
| Mandatory Maps Within 25% of Optimum | 9/9 |
| Total Mandatory Reference Turns | 91 |
| Total Mandatory Simulation Turns | 93 |
| Additional Mandatory Turns | 2 |
| Aggregate Mandatory Optimization Gap | 2.20% |
| Challenger Drones Delivered | 25/25 |
| Challenger Optimization Gap | 18.60% |
| Total Maps Completed | 10/10 |

### Performance Comparison

```text
                          Optimal / Actual

Easy 1                    4 / 4
Easy 2                    4 / 4
Easy 3                    4 / 4

Medium 1                  8 / 8
Medium 2                 10 / 10
Medium 3                  6 / 7

Hard 1                   13 / 13
Hard 2                   16 / 16
Hard 3                   26 / 27

Challenger               43 / 51
```

### Performance Analysis

All nine mandatory maps were completed successfully in the recorded test runs.

Seven mandatory maps reached the exact reference optimum.

The remaining two mandatory maps required only one additional simulation turn each.

Across the mandatory benchmark suite, the implementation required 93 simulation turns compared with the combined theoretical reference of 91 turns.

This represents an aggregate optimization gap of approximately 2.20%.

The Challenger map was completed with all 25 drones reaching the destination in 51 turns. This demonstrates the ability of the simulation to handle more complex network topologies and larger fleets.

However, the Challenger result does not satisfy the official bonus requirement of exactly 43 turns.

## Testing

The project was tested using maps covering different network structures and movement constraints.

### Test Scenarios

| Scenario | Purpose |
|---|---|
| Linear Path | Basic movement and sequential scheduling. |
| Simple Fork | Alternative path discovery. |
| Basic Capacity | Zone and connection capacity constraints. |
| Dead End Trap | Avoiding inefficient or unusable paths. |
| Circular Loop | Handling cyclic graph structures. |
| Priority Puzzle | Handling priority and restricted zones. |
| Maze Nightmare | Routing through complex graph structures. |
| Capacity Hell | Managing shared resources and congestion. |
| Ultimate Challenge | Coordinating larger drone fleets. |
| The Impossible Dream | Stress-testing routing and scheduling strategies. |

## Technical Challenges

The main technical challenge was coordinating multiple drones within a shared network rather than finding a shortest path for a single drone.

Additional challenges included:

- Representing graph structures without external graph libraries.
- Reconstructing paths from predecessor information.
- Finding alternative routes.
- Managing shared zone and connection capacities.
- Coordinating simultaneous movements.
- Handling restricted zones across multiple turns.
- Preventing movement conflicts.
- Reducing unnecessary waiting.
- Maintaining consistent drone and graph states.
- Separating routing logic from simulation logic.
- Designing a modular, object-oriented architecture.

## Current Limitations

The current implementation has several optimization limitations:

- Round-robin distribution does not account for every difference in route throughput.
- Alternative routes may share bottleneck zones or connections.
- Locally efficient movements may not produce a globally optimal schedule.
- The optimization strategy does not guarantee the theoretical minimum makespan.
- The Challenger map requires eight additional turns compared with its theoretical optimum.

These limitations concern optimization quality rather than a claim of universal algorithmic optimality.

## Future Improvements

Potential improvements include:

- Capacity-aware route assignment.
- Dynamic route selection.
- Congestion-aware pathfinding.
- Time-expanded graph representations.
- Maximum-flow and minimum-cost-flow algorithms.
- Reservation-based movement scheduling.
- Improved bottleneck detection.
- Automated performance regression tests.
- Graphical network visualization.
- CPU and memory profiling.
- Further Challenger map optimization.

## Technologies

| Technology | Purpose |
|---|---|
| Python | Core implementation |
| Object-Oriented Programming | Software architecture |
| Graph Theory | Network representation |
| Dijkstra's Algorithm | Shortest-path discovery |
| Heuristic Algorithms | Routing and scheduling optimization |
| ANSI Terminal Colors | Visual representation |
| Mypy | Static type checking |
| Flake8 | Code quality and style checking |
| Makefile | Development automation |
| Git | Version control |

## Skills Developed

This project provided practical experience in:

- Graph algorithms.
- Data structures.
- Algorithm design.
- Multi-agent routing.
- Resource allocation.
- State management.
- Movement scheduling.
- Discrete simulation.
- Performance optimization.
- Object-oriented software architecture.
- Input parsing and validation.
- Debugging and problem-solving.
- Static type checking.
- Technical documentation.

## Resources

### Algorithms and Graph Theory

- [Dijkstra's Algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- [Graph Theory](https://en.wikipedia.org/wiki/Graph_theory)
- [Shortest Path Problem](https://en.wikipedia.org/wiki/Shortest_path_problem)
- [Maximum Flow Problem](https://en.wikipedia.org/wiki/Maximum_flow_problem)
- [Multi-Agent Pathfinding](https://en.wikipedia.org/wiki/Multi-agent_pathfinding)

### Python and Development Tools

- [Python Documentation](https://docs.python.org/3/)
- [Python Data Structures](https://docs.python.org/3/tutorial/datastructures.html)
- [Python Typing Documentation](https://docs.python.org/3/library/typing.html)
- [Python Classes](https://docs.python.org/3/tutorial/classes.html)
- [PEP 8 — Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [PEP 257 — Docstring Conventions](https://peps.python.org/pep-0257/)
- [Mypy Documentation](https://mypy.readthedocs.io/)
- [Flake8 Documentation](https://flake8.pycqa.org/)
- [GNU Make Documentation](https://www.gnu.org/software/make/manual/)

### AI Usage

AI tools were used as learning and development assistants throughout the project.

AI assistance included:

- Understanding Dijkstra's algorithm and graph theory.
- Explaining algorithm relaxation and path reconstruction.
- Discussing graph data structures.
- Preparing technical documentation and improving its English wording.

AI was used to support algorithmic understanding, implementation discussions, and documentation.

The project must be understood, tested, and explainable by its author during peer evaluation.

## Conclusion

Fly-in explores the relationship between graph algorithms, multi-agent coordination, shared resource management, and performance optimization.

The recorded implementation successfully completed all mandatory benchmark maps, achieved seven exact optimal solutions, and completed the optional Challenger map.

The project demonstrates how shortest-path algorithms can be combined with simulation and scheduling techniques to address more complex multi-agent routing problems.

## Acknowledgments

42 School — Common Core Curriculum.