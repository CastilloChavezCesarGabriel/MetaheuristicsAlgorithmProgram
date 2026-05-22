import numpy as np
from problems.base_problem import BaseProblem


class TspProblem(BaseProblem):
    def __init__(self, n: int, coords: list[tuple]):
        self.n      = n
        self.coords = np.asarray(coords, dtype=float)

    @property
    def bounds(self):
        return None

    def evaluate(self, solution) -> float:
        route = [int(round(c)) % self.n for c in solution]
        total = 0.0
        for i in range(self.n):
            a = self.coords[route[i]]
            b = self.coords[route[(i + 1) % self.n]]
            total += float(np.linalg.norm(a - b))
        return total

    def generate_random_solution(self):
        return np.random.permutation(self.n).astype(float)

    def get_param_schema(self) -> list[dict]:
        return [
            {'name': 'n',        'type': 'int', 'min': 3, 'default': 5,
             'description': 'Numero de ciudades (n >= 3)'},
            {'name': 'coords_x', 'type': 'str',
             'default': '0, 100, 100, 0, 50',
             'description': 'Coordenadas X separadas por coma'},
            {'name': 'coords_y', 'type': 'str',
             'default': '0, 0, 100, 100, 50',
             'description': 'Coordenadas Y separadas por coma'},
        ]

    def validate_solution(self, solution) -> bool:
        route = [int(round(c)) % self.n for c in solution]
        return len(set(route)) == self.n
