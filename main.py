
import sys

from parser import MapParser
from algorithms.alternative_routes import find_alternative_routes
from simulation.simulation import Simulation


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 main.py <map_file>")
        return

    try:
        data = MapParser(sys.argv[1]).parse()

        paths = find_alternative_routes(
            data.graph,
            data.start_hub,
            data.end_hub,
            data.nb_drones
        )

        if not paths:
            raise ValueError("No path to destination")

        sim = Simulation(data, paths)
        sim.run()

    except (OSError, ValueError) as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    main()