from classes import Zone, Graph, MapData


class MapParser:
    """Read and parse drone network map files."""
    def __init__(self, filename: str) -> None:
        """Initialize the parser with a map filename."""
        self.filename = filename

    def read_map(self) -> list[tuple[int, str]]:
        """Read map lines from the file."""
        lines: list[tuple[int, str]] = []
        with open(self.filename, "r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                line = line.split("#", 1)[0].strip()
                if not line:
                    continue
                lines.append((line_number, line))
        return lines

    def parse_map(self, lines: list[tuple[int, str]]) -> MapData:
        """Parse map lines into a MapData object."""
        nb_drones: int | None = None
        start_hub: str | None = None
        end_hub: str | None = None
        graph = Graph()
        if not lines:
            raise ValueError("Empty map file")
        first_line_number, first_line = lines[0]
        if first_line.split(":", 1)[0].strip() != "nb_drones":
            raise ValueError(f"Line {first_line_number}: "
                             "nb_drones must be the first directive")
        for line_number, line in lines:
            try:
                key, value = line.split(":", 1)
                value = value.strip()
                if key == "nb_drones":
                    if nb_drones is not None:
                        raise ValueError("Duplicate nb_drones definition")
                    try:
                        nb_drones = int(value)
                    except ValueError:
                        raise ValueError("Invalid drone count: must be an integer")
                    if nb_drones <= 0:
                        raise ValueError("Invalid drone count: must be positive")
                elif key in ["start_hub", "hub", "end_hub"]:
                    parts = value.split()
                    if len(parts) < 3:
                        raise ValueError("Invalid hub format: expected name x y")
                    metadata = {}
                    name = parts[0]
                    if "-" in name:
                        raise ValueError(f"Invalid hub name: {name}")
                    if key == "start_hub":
                        if start_hub is not None:
                            raise ValueError("Duplicate start_hub definition")
                        start_hub = name
                    elif key == "end_hub":
                        if end_hub is not None:
                            raise ValueError("Duplicate end_hub definition")
                        end_hub = name 
                    x = int(parts[1])
                    y = int(parts[2])
                    metadata_text = " ".join(parts[3:])
                    if metadata_text:
                        if not metadata_text.startswith("["):
                            raise ValueError("Invalid hub metadata brackets")
                        if not metadata_text.endswith("]"):
                            raise ValueError("Invalid hub metadata brackets")
                        if metadata_text.count("[") != 1 or metadata_text.count("]") != 1:
                            raise ValueError("Invalid hub metadata brackets")
                        metadata_text = metadata_text[1:-1]
                    valid_keys = {"zone", "color", "max_drones"}
                    for item in metadata_text.split():
                        if item.count("=") != 1:
                            raise ValueError(f"Invalid metadata: {item}")
                        meta_key, meta_value = item.split("=", 1)
                        if meta_key not in valid_keys:
                            raise ValueError(f"Unknown hub metadata: {meta_key}")
                        if not meta_value:
                            raise ValueError(f"Empty metadata value: {meta_key}")
                        if meta_key in metadata:
                            raise ValueError(f"Duplicate metadata key: {meta_key}")
                        metadata[meta_key] = meta_value
                    zone_type = metadata.get("zone", "normal")
                    if key in ["start_hub", "end_hub"]:
                        max_drones = 1
                    else:
                        max_drones = int(metadata.get("max_drones", "1"))
                    color = metadata.get("color", "none")
                    zone = Zone(name, x, y, zone_type, max_drones, color)
                    graph.add_zone(zone)
                elif key == "connection":
                    parts = value.split()
                    if not 1 <= len(parts) <= 2:
                        raise ValueError("Invalid connection format")
                    capacity = 1
                    connection_names = parts[0]
                    if len(parts) > 1:
                        if not parts[1].startswith("[") or not parts[1].endswith("]"):
                            raise ValueError("Invalid connection metadata  brackets")
                        if parts[1].count("[") != 1 or parts[1].count("]") != 1:
                            raise ValueError("Invalid connection metadata brackets")
                        meta_data = parts[1][1:-1]
                        if meta_data.count("=") != 1:
                            raise ValueError("Invalid connection metadata")
                        meta_data_key, meta_data_value = meta_data.split("=", 1)
                        if not meta_data_value:
                            raise ValueError("EMpty max_linek capacity value")
                        if meta_data_key != "max_link_capacity":
                            raise ValueError(f"Unknown connection meta_data_key {meta_data_key}")
                        capacity = int(meta_data_value)
                    if connection_names.count("-") != 1:
                        raise ValueError("Invalid connection: expected name1-name2")
                    from_zone, to_zone = connection_names.split("-")
                    if not from_zone or not to_zone:
                        raise ValueError("Invalid connection: empty zone name")
                    graph.add_connections(from_zone, to_zone, capacity)
                else:
                    raise ValueError(f"Unknown directive: {key}")
            except (ValueError, IndexError, KeyError) as error:
                raise ValueError(f"Line {line_number}: {error}") from error
        if nb_drones is None:
            raise ValueError("Missing nb_drones definition")
        if start_hub is None:
            raise ValueError("Missing start_hub definition")
        if end_hub is None:
            raise ValueError("Missing end_hub definition")
        return MapData(graph, nb_drones, start_hub, end_hub)

    def parse(self) -> MapData:
        """Read and parse the map file."""
        lines = self.read_map()
        return self.parse_map(lines)

