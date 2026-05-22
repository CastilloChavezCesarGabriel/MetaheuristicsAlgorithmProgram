import numpy as np
from problems.base_problem import BaseProblem
from utils.parser import parse_expression, evaluate_expression


class CategoricalProblem(BaseProblem):
    def __init__(self, expression: str, dimensions: int,
                 bounds: list[tuple], num_options: int,
                 option_values: list[float]):
        self.expression_str = expression
        self.dimensions     = dimensions
        self._cont_bounds   = bounds
        self.num_options    = num_options
        self.option_values  = list(option_values)
        var_names = [f'x{i+1}' for i in range(dimensions)] + ['D']
        self._expr, self._symbols = parse_expression(expression, var_names)

    @property
    def bounds(self) -> list[tuple]:
        return self._cont_bounds + [(0.0, float(self.num_options - 1))]

    def evaluate(self, solution) -> float:
        sol   = list(solution)
        cat   = int(round(sol[-1])) % self.num_options
        D_val = self.option_values[cat]
        vals  = sol[:-1] + [D_val]
        return evaluate_expression(self._expr, self._symbols, vals)

    def generate_random_solution(self):
        cont = np.array([np.random.uniform(lo, hi)
                         for lo, hi in self._cont_bounds])
        cat  = np.array([float(np.random.randint(0, self.num_options))])
        return np.concatenate([cont, cat])

    def get_param_schema(self) -> list[dict]:
        return [
            {'name': 'expression',     'type': 'str',   'default': 'x1**2 + D',
             'description': 'Expresion (use D como variable categorica)'},
            {'name': 'dimensions',     'type': 'int',   'min': 1, 'max': 2, 'default': 1,
             'description': 'Variables continuas (1 o 2)'},
            {'name': 'lower_bound_x1', 'type': 'float', 'default': -5.0,
             'description': 'Limite inferior x1'},
            {'name': 'upper_bound_x1', 'type': 'float', 'default': 5.0,
             'description': 'Limite superior x1'},
            {'name': 'lower_bound_x2', 'type': 'float', 'default': -5.0,
             'description': 'Limite inferior x2 (si dims=2)'},
            {'name': 'upper_bound_x2', 'type': 'float', 'default': 5.0,
             'description': 'Limite superior x2 (si dims=2)'},
            {'name': 'num_options',    'type': 'int',   'min': 2, 'max': 10, 'default': 4,
             'description': 'Numero de opciones categoricas (2-10)'},
            {'name': 'option_values',  'type': 'str',
             'default': '-3.0, -1.0, 7.0, -9.0',
             'description': 'Valor numerico de cada opcion (separados por coma)'},
        ]

    def validate_solution(self, solution) -> bool:
        sol = list(solution)
        if len(sol) != self.dimensions + 1:
            return False
        for i, (lo, hi) in enumerate(self._cont_bounds):
            if not (lo <= sol[i] <= hi):
                return False
        return 0 <= int(round(sol[-1])) < self.num_options
