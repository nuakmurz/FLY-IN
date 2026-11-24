from classes import Graph

def get_travel_costs(graph: Graph, destination: str) -> int:
    if graph.zones[destination].zone_type == "restricted":
        return 2
    else:
        return 1