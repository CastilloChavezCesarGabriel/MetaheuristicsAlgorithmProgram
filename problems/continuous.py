import numpy as np

from problems.base_problem import BaseProblem
from utils.parser import parse_expression, evaluate_expression


class ContinuousProblem(BaseProblem):

    def __init__(self, expression: str, dimensions: int, bounds: list[tuple]):
        self.expression_str = expression
        self.dimensions = dimensions
        self._bounds = bounds

        var_names = [f'x{i+1}' for i in range(dimensions)]
        self._expr, self._symbols = parse_expression(expression, var_names)

    @property
    def bounds(self) -> list[tuple]:
        return self._bounds

    def evaluate(self, solution) -> float:
        return evaluate_expression(self._expr, self._symbols, list(solution))

    def generate_random_solution(self) -> np.ndarray:
        return np.array([
            np.random.uniform(lb, ub)
            for lb, ub in self._bounds
        ])

    def get_param_schema(self) -> list[dict]:
        return [
            {
                'name': 'expression',
                'type': 'str',
                'default': 'x1**2',
                'description': 'Expresión matemática con variables x1 (y x2 si dimensions=2)'
            },
            {
                'name': 'dimensions',
                'type': 'int',
                'min': 1,
                'max': 2,
                'default': 1,
                'description': 'Número de variables (1 o 2)'
            },
            {
                'name': 'lower_bound_x1',
                'type': 'float',
                'default': -5.0,
                'description': 'Límite inferior de x1'
            },
            {
                'name': 'upper_bound_x1',
                'type': 'float',
                'default': 5.0,
                'description': 'Límite superior de x1'
            },
            {
                'name': 'lower_bound_x2',
                'type': 'float',
                'default': -5.0,
                'description': 'Límite inferior de x2 (solo si dimensions=2)'
            },
            {
                'name': 'upper_bound_x2',
                'type': 'float',
                'default': 5.0,
                'description': 'Límite superior de x2 (solo si dimensions=2)'
            },
        ]

    def validate_solution(self, solution) -> bool:
        if len(solution) != self.dimensions:
            return False
        return all(lb <= solution[i] <= ub for i, (lb, ub) in enumerate(self._bounds))
