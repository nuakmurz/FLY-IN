class Zone:
    """Represent a zone in the drone network."""
    def __init__(self, name: str, x: int, y: int,
                 zone_type: str = "normal",
                 max_drones: int = 1,
                 color: str = "none") -> None:
        """Initialize a zone with its coordinates, type, and capacity."""
        if max_drones <= 0:
            raise ValueError("max_drones must be positive")
        if zone_type not in ["normal", "restricted", "priority", "blocked"]:
            raise ValueError(f"Invalid zone type: {zone_type}")
        self.name = name
        self.x = x
        self.y = y
        self.zone_type = zone_type
        self.max_drones = max_drones
        self.color = color


class Drone:
    """Represent a drone and track its movement along a path."""
    def __init__(self, drone_id: int, path: list[str]) -> None:
        """Initialize a drone with its ID, path, and movement state."""
        if not path:
            raise ValueError("Drone path cannot be empty")
        self.drone_id = drone_id
        self.path = path
        self.path_index = 0
        self.remaining_turns = 0
        self.finished = len(path) == 1


class Graph:
    """Manage zones and bidirectional connections between them."""
    def __init__(self) -> None:
        """Initialize empty dictionaries for zones and connections."""
        self.zones: dict[str, Zone] = {}
        self.connections: dict[str, dict[str, int]] = {}

    def add_zone(self, zone: Zone) -> None:
        """Add a new zone to the graph, rejecting duplicate names."""
        if zone.name in self.zones:
            raise ValueError(f"Duplicate hub name: {zone.name}")
        self.zones[zone.name] = zone
        self.connections[zone.name] = {}

    def add_connections(self, from_zone: str,
                        to_zone: str,
                        capacity: int = 1) -> None:
        """Add a bidirectional connection with capacity validation."""
        if from_zone not in self.zones:
            raise ValueError(f"Unknown hub: {from_zone}")
        if to_zone not in self.zones:
            raise ValueError(f"Unknown hub: {to_zone}")
        if capacity <= 0:
            raise ValueError("max_link_capacity must be positive")
        if to_zone in self.connections[from_zone]:
            raise ValueError(f"Duplicate connection: {from_zone}-{to_zone}")
        if from_zone == to_zone:
            raise ValueError(f"Self-connection is not allowed: {from_zone}")
        self.connections[from_zone][to_zone] = capacity
        self.connections[to_zone][from_zone] = capacity


class MapData:
    """Store the parsed map, drone count, and start/end zones."""
    def __init__(self, graph: Graph,
                 nb_drones: int,
                 start_hub: str,
                 end_hub: str) -> None:
        """Store the graph, drone count, and start and end hub names."""
        self.graph = graph
        self.nb_drones = nb_drones
        self.start_hub = start_hub
        self.end_hub = end_hub
