from classes import Drone, Graph, MapData


COLORS = {
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "purple": "\033[35m",
    "cyan": "\033[36m",
    "orange": "\033[38;5;208m",
    "brown": "\033[38;5;130m",
    "gold": "\033[38;5;220m",
    "lime": "\033[92m",
    "magenta": "\033[35m",
    "violet": "\033[38;5;177m",
}


class Simulation:
    """Manage drone movement and turn-based simulation."""
    def __init__(self, map_data: MapData,
                 paths: list[list[str]]) -> None:
        """Initialize the simulation with map data and paths."""
        self.paths = paths
        self.map_data = map_data
        self.drones: list[Drone] = []

    def distribute(self) -> list[Drone]:
        """Distribute drones across available paths."""
        if not self.paths:
            raise ValueError("No available paths")
        self.drones = []
        for i in range(self.map_data.nb_drones):
            path = self.paths[i % len(self.paths)]
            self.drones.append(Drone(i + 1, path))
        return self.drones


    def get_next_zone(self, drone: Drone) -> str | None:
        """Return the next zone in the drone's path."""
        if drone.path_index >= len(drone.path) - 1:
            return None
        return drone.path[drone.path_index + 1]


    
    def schedule_turn(self) -> list[tuple[int, str, str]]:
        """Plan safe simultaneous drone movements."""
        graph = self.map_data.graph
        arrivals: dict[str, int] = {}
        for drone in self.drones:
            if drone.remaining_turns > 0:
                next_zone = self.get_next_zone(drone)
                if next_zone is None:
                    raise ValueError("Flying drone has no destination")
                arrivals[next_zone] = arrivals.get(next_zone, 0) + 1
        planned_moves: list[tuple[int, str, str]] = []
        for drone in sorted(
            self.drones,
            key=lambda d: d.path_index,
            reverse=True
        ):
            if drone.finished or drone.remaining_turns > 0:
                continue
            next_zone = self.get_next_zone(drone)
            if next_zone is None:
                continue
            if graph.zones[next_zone].zone_type == "blocked":
                continue
            current = drone.path[drone.path_index]
            planned_moves.append((drone.drone_id, current, next_zone))
        while True:
            changed = False
            for i in range(len(planned_moves) - 1, -1, -1):
                _, source, target = planned_moves[i]
                usage = count_link_usage(planned_moves, source, target)

                if usage > graph.connections[source][target]:
                    planned_moves.pop(i)
                    changed = True
                    break
            if changed:
                continue
            for name, zone in graph.zones.items():
                if name in (self.map_data.start_hub, self.map_data.end_hub):
                    continue
                occupied = count_drones_in_zone(self.drones, name)
                incoming = count_incoming_drones(graph, planned_moves, name)
                leaving = count_outgoing_drones(planned_moves, name)
                if (
                    occupied + arrivals.get(name, 0)
                    + incoming - leaving > zone.max_drones
                ):
                    for i in range(len(planned_moves) - 1, -1, -1):
                        if (
                            planned_moves[i][2] == name
                            and zone.zone_type != "restricted"
                        ):
                            planned_moves.pop(i)
                            changed = True
                            break
                    if not changed:
                        raise ValueError(f"No room for arrival at {name}")
                    break
            if changed:
                continue
            for name, zone in graph.zones.items():
                if zone.zone_type != "restricted":
                    continue
                if name == self.map_data.end_hub:
                    continue
                occupied = count_drones_in_zone(self.drones, name)
                occupied += arrivals.get(name, 0)
                occupied -= count_outgoing_drones(planned_moves, name)
                flights = [
                    i for i, move in enumerate(planned_moves)
                    if move[2] == name
                ]
                if occupied + len(flights) > zone.max_drones:
                    arriving_to_end = any(
                        drone.remaining_turns > 0
                        and drone.path[drone.path_index + 1:]
                        == [name, self.map_data.end_hub]
                        for drone in self.drones
                    )

                    if (
                        zone.max_drones == 1
                        and occupied == 1
                        and arrivals.get(name, 0) == 1
                        and len(flights) == 1
                        and arriving_to_end
                    ):
                        continue

                    if not flights:
                        raise ValueError(f"No room at {name}")
                    planned_moves.pop(flights[-1])
                    changed = True
                    break
            if not changed:
                return planned_moves


    def run(self) -> None:
        """Run and print the drone simulation."""
        self.distribute()

        while not all(drone.finished for drone in self.drones):
            planned = self.schedule_turn()
            moving = {drone_id for drone_id, _, _ in planned}
            flying = {d.drone_id for d in self.drones
                    if d.remaining_turns > 0}
            if not moving and not flying:
                raise ValueError("Deadlock: no drone can move")
            output: list[str] = []
            for drone in self.drones:
                if drone.drone_id not in moving | flying:
                    continue
                current = drone.path[drone.path_index]
                next_zone = self.get_next_zone(drone)
                if next_zone is None:
                    raise ValueError("Drone has no destination")
                self.drone_moves(drone)
                if drone.drone_id in moving and drone.remaining_turns > 0:
                    move = f"D{drone.drone_id}-{current}-{next_zone}"
                else:
                    move = f"D{drone.drone_id}-{next_zone}"
                zone = self.map_data.graph.zones[next_zone]
                color = COLORS.get(zone.color, "")
                if color:
                    move = f"{color}{move}\033[0m"
                output.append(move)
            print(" ".join(output))


    def drone_moves(self, drone: Drone) -> None:
        if drone.finished:
            return None
        if drone.remaining_turns > 0:
            drone.remaining_turns = 0
            drone.path_index += 1
            if drone.path_index  == len(drone.path) - 1:
                drone.finished = True
            return None
        next_zone = self.get_next_zone(drone)
        if next_zone is None:
            return
        zone_type = self.map_data.graph.zones[next_zone].zone_type
        if zone_type == "blocked":
            return None
        elif zone_type == "restricted":
            drone.remaining_turns = 1
        elif zone_type == "normal" or zone_type == "priority":
            drone.path_index += 1
            if drone.path_index  == len(drone.path) - 1:
                drone.finished = True
        return None
    

def count_drones_in_zone(drones: list[Drone], zone_name: str) -> int:
    count = 0
    for drone in drones:
        if drone.remaining_turns > 0 or drone.finished:
            continue
        if drone.path[drone.path_index] == zone_name:
            count += 1
    return count


def count_incoming_drones(graph: Graph,
                          planned_moves: list[tuple[int, str, str]],
                          zone_name: str) -> int:
    count = 0
    for arg in planned_moves:
        if (arg[2] == zone_name
            and
            graph.zones[zone_name].zone_type != "restricted"
            ):
            count += 1
    return count


def count_outgoing_drones(planned_moves: list[tuple[int, str, str]],
                          zone_name: str) -> int:
    count = 0
    for arg in planned_moves:
        if arg[1] == zone_name:
            count += 1
    return count


def validate_moves(map_data: MapData, drones: list[Drone],
                   planned_moves: list[tuple[int, str, str]],
                   arrivals_count: dict[str, int]
                   ) -> bool:
    graph = map_data.graph
    for zone_name, zone in graph.zones.items():
        if zone_name == map_data.start_hub or zone_name == map_data.end_hub:
            continue
        curr = count_drones_in_zone(drones, zone_name)
        incoming = (count_incoming_drones(graph, planned_moves, zone_name)
                    +
                    arrivals_count.get(zone_name, 0))
        outgoing = count_outgoing_drones(planned_moves, zone_name)
        final_count = curr + incoming - outgoing
        if final_count > zone.max_drones:
            return False
    return True


def count_link_usage(planned_moves: list[tuple[int, str, str]],
                     from_zone: str, to_zone: str) -> int:
    count = 0
    for move in planned_moves:
        if move[1] == from_zone and move[2] == to_zone or \
        move[1] == to_zone and move[2] == from_zone:
            count += 1
    return count


def validate_link_capacity(graph: Graph,
                           planned_moves: list[tuple[int, str, str]]
                           ) -> bool:
    for _, from_zone, to_zone in planned_moves:
        usage = count_link_usage(planned_moves, from_zone, to_zone)
        if usage > graph.connections[from_zone][to_zone]:
            return False
    return True