"""Central registry mapping algorithm code to class.

Replaces the 5-branch if-ladder previously copied in gui/app.py
and config/param_definitions.py.
"""
from algorithms.genetic_algorithm      import GeneticAlgorithm
from algorithms.pso                    import PSO
from algorithms.aco                    import ACO
from algorithms.ais                    import AIS
from algorithms.differential_evolution import DifferentialEvolution

ALGORITHM_CLASSES = {
    'ga':  GeneticAlgorithm,
    'pso': PSO,
    'aco': ACO,
    'ais': AIS,
    'de':  DifferentialEvolution,
}
