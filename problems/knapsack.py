import numpy as np
from problems.base_problem import BaseProblem


class KnapsackProblem(BaseProblem):
    def __init__(self, n: int, weights: list, values: list,
                 W: float, alpha: float):
        self.n        = n
        self._weights = np.asarray(weights, dtype=float)
        self._values  = np.asarray(values,  dtype=float)
        self.W        = float(W)
        self.alpha    = float(alpha)

    @property
    def bounds(self):
        return [(0.0, 1.0)] * self.n

    def evaluate(self, solution) -> float:
        x   = np.asarray(solution, dtype=float)
        val = float(np.dot(self._values, x))
        exc = max(0.0, float(np.dot(self._weights, x)) - self.W)
        return val - self.alpha * exc

    def generate_random_solution(self):
        return np.random.randint(0, 2, size=self.n).astype(float)

    def get_param_schema(self) -> list[dict]:
        return [
            {'name': 'n',       'type': 'int',   'min': 2,     'default': 5,
             'description': 'Numero de objetos (n >= 2)'},
            {'name': 'weights', 'type': 'str',
             'default': '2.0, 3.0, 1.5, 4.0, 2.5',
             'description': 'Pesos separados por coma'},
            {'name': 'values',  'type': 'str',
             'default': '3.0, 4.0, 1.0, 5.0, 2.0',
             'description': 'Valores separados por coma'},
            {'name': 'W',       'type': 'float', 'min': 0.001, 'default': 7.0,
             'description': 'Capacidad maxima (W > 0)'},
            {'name': 'alpha',   'type': 'float', 'min': 0.001, 'default': 10.0,
             'description': 'Factor de penalizacion (alpha > 0)'},
        ]

    def validate_solution(self, solution) -> bool:
        x = np.asarray(solution)
        return len(x) == self.n and all(0.0 <= v <= 1.0 for v in x)
