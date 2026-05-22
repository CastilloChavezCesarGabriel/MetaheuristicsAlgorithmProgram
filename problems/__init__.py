"""Central registry mapping problem code to class plus a problem-type detector.

Replaces the duplicated isinstance ladders in every algorithm's initialize()
and the if-chain in gui/app.py / config/param_definitions.py.
"""
from problems.continuous  import ContinuousProblem
from problems.knapsack    import KnapsackProblem
from problems.categorical import CategoricalProblem
from problems.tsp         import TspProblem

PROBLEM_CLASSES = {
    'continuous':  ContinuousProblem,
    'knapsack':    KnapsackProblem,
    'categorical': CategoricalProblem,
    'tsp':         TspProblem,
}


def prob_type_of(problem):
    """Return the registry code ('continuous', 'knapsack', ...) for a problem instance."""
    for code, cls in PROBLEM_CLASSES.items():
        if isinstance(problem, cls):
            return code
    return 'continuous'
