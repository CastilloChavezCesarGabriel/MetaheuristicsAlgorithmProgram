from abc import ABC, abstractmethod


class BaseAlgorithm(ABC):

    @abstractmethod
    def initialize(self, problem, params: dict, maximize: bool):
        """Prepara la población inicial. Recibe el problema instanciado,
        los parámetros del algoritmo, y la dirección de optimización."""
        pass

    @abstractmethod
    def step(self) -> dict:
        """Ejecuta UNA iteración. Retorna:
        {
            'best_fitness': float,
            'avg_fitness': float,
            'best_solution': any,
            'iteration': int
        }
        """
        pass

    @abstractmethod
    def get_param_schema(self, problem_type: str) -> list[dict]:
        """Retorna parámetros configurables según el tipo de problema.
        problem_type: 'continuous' | 'knapsack' | 'categorical' | 'tsp'"""
        pass

    @property
    @abstractmethod
    def is_finished(self) -> bool:
        """True si el algoritmo completó todas sus iteraciones."""
        pass
