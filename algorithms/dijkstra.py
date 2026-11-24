from classes import Graph
import heapq
from algorithms.costs import get_travel_costs


class PathFinder:
    """Find optimal paths through the drone network."""
    def __init__(self, graph: Graph) -> None:
        """Initialize the pathfinder with a graph."""
        self.graph = graph

    def initialize_distances(
        self,
        start: str
    ) -> dict[str, float]:
        """Initialize distances from the start zone to all other zones."""
        distances: dict[str, float] = {}
        for node in self.graph.zones:
            distances[node] = float("inf")

        distances[start] = 0
        return distances


    def dijkstra(
        self,
        start: str,
        end: str
    ) -> list[str]:
        """Find the shortest path, preferring priority zones on ties."""
        if start not in self.graph.zones or end not in self.graph.zones:
            return []
        distances = self.initialize_distances(start)
        priority_counts: dict[str, int] = {
            node: 0 for node in self.graph.zones
        }
        parent: dict[str, str | None] = {start: None}

        heap: list[tuple[float, int, str]] = []
        heapq.heappush(heap, (0, 0, start))

        while heap:
            current_cost, neg_priority, current = heapq.heappop(heap)

            if current_cost > distances[current]:
                continue
            if (
                current_cost == distances[current]
                and -neg_priority < priority_counts[current]
                ):
                continue

            if current == end:
                break

            for neighbor in self.graph.connections[current]:
                if self.graph.zones[neighbor].zone_type == "blocked":
                    continue
                travel_costs = get_travel_costs(self.graph, neighbor)
                new_cost = current_cost + travel_costs
                new_priority = priority_counts[current]
                if self.graph.zones[neighbor].zone_type == "priority":
                    new_priority += 1   
                better_cost = new_cost < distances[neighbor]
                better_priority = (
                    new_cost == distances[neighbor] and 
                    new_priority > priority_counts[neighbor]
                )
                if better_cost or better_priority:
                    distances[neighbor] = new_cost
                    priority_counts[neighbor] = new_priority
                    parent[neighbor] = current
                    heapq.heappush(heap, (new_cost, -new_priority, neighbor))

        if end not in parent:
            return []

        path = []
        current = end

        while current != start:
            path.append(current)
            previous = parent[current]
            if previous is None:
                return []
            current = previous

        path.append(start)
        path.reverse()

        return path
