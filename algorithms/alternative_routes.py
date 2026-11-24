from classes import Graph
from algorithms.dijkstra import PathFinder


def copy_graph(graph: Graph) -> Graph:
    new_graph = Graph()
    new_graph.zones = graph.zones.copy()
    new_graph.connections = {node: neighbors.copy()
            for node, neighbors in graph.connections.items()}
    return new_graph


def find_alternative_routes(graph: Graph, start: str, end: str, max_routes: int) -> list[list[str]]:
    if max_routes <= 0:
        return []
    pathfinder = PathFinder(graph)
    path_1 = pathfinder.dijkstra(start, end)
    paths = [path_1]
    if not path_1:
        return []
    else:
        for from_zone, to_zone in zip(path_1, path_1[1:]):
            if len(paths) >= max_routes:
                break 
            temp_graph = copy_graph(graph)
            del temp_graph.connections[from_zone][to_zone]
            del temp_graph.connections[to_zone][from_zone]
            alternative = PathFinder(temp_graph).dijkstra(start, end)
            if alternative and alternative not in paths:
                paths.append(alternative)
    return paths