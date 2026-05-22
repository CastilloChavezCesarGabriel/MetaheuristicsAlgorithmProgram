from config.defaults import DEFAULTS

_IMPLEMENTED = {
    ('continuous',  'ga'),  ('continuous',  'pso'), ('continuous',  'aco'),
    ('continuous',  'ais'), ('continuous',  'de'),
    ('knapsack',    'ga'),  ('knapsack',    'pso'), ('knapsack',    'aco'),
    ('knapsack',    'ais'), ('knapsack',    'de'),
    ('categorical', 'ga'),  ('categorical', 'pso'), ('categorical', 'aco'),
    ('categorical', 'ais'), ('categorical', 'de'),
    ('tsp',         'ga'),  ('tsp',         'pso'), ('tsp',         'aco'),
    ('tsp',         'ais'), ('tsp',         'de'),
}


def is_implemented(problem: str, algorithm: str) -> bool:
    return (problem, algorithm) in _IMPLEMENTED


def get_param_schema(problem: str, algorithm: str) -> tuple[list[dict], list[dict]]:
    if not is_implemented(problem, algorithm):
        return [], []

    prob_schema = _get_problem_schema(problem)
    algo_schema = _get_algorithm_schema(algorithm, problem)

    algo_defaults = DEFAULTS.get(problem, {}).get(algorithm, {})
    for param in algo_schema:
        if param['name'] in algo_defaults:
            param['default'] = algo_defaults[param['name']]

    return prob_schema, algo_schema


def _get_problem_schema(problem: str) -> list[dict]:
    if problem == 'continuous':
        from problems.continuous import ContinuousProblem
        return ContinuousProblem('x1', 1, [(-1.0, 1.0)]).get_param_schema()
    if problem == 'knapsack':
        from problems.knapsack import KnapsackProblem
        return KnapsackProblem(5, [2, 3, 1, 4, 2], [3, 4, 1, 5, 2], 7, 10).get_param_schema()
    if problem == 'categorical':
        from problems.categorical import CategoricalProblem
        return CategoricalProblem('x1**2+D', 1, [(-5, 5)], 4, [-3, -1, 7, -9]).get_param_schema()
    if problem == 'tsp':
        from problems.tsp import TspProblem
        return TspProblem(5, [(0, 0), (1, 0), (1, 1), (0, 1), (0.5, 0.5)]).get_param_schema()
    return []


def _get_algorithm_schema(algorithm: str, problem_type: str) -> list[dict]:
    from algorithms import ALGORITHM_CLASSES
    cls = ALGORITHM_CLASSES.get(algorithm)
    if cls is None:
        return []
    return cls().get_param_schema(problem_type)
