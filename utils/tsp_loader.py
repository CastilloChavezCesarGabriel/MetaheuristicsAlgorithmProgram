import os

_DIR = os.path.join(os.path.dirname(__file__), '..', 'assets', 'tsp_datasets')


def load_dataset(name: str) -> tuple[int, list[tuple[float, float]]]:
    """Load a TSP dataset by name. Returns (n, list of (x, y) tuples)."""
    path = os.path.join(_DIR, f'{name}.txt')
    coords = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            coords.append((float(parts[0]), float(parts[1])))
    return len(coords), coords
