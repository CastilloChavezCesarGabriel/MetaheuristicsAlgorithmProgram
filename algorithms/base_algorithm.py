from abc import ABC, abstractmethod


class BaseAlgorithm(ABC):

    def _prepare(self, problem, params: dict, maximize: bool, iters_key: str):
        """Common setup every algorithm needs at the top of initialize().

        Stores problem, params, orientation, an iteration counter, the
        total-iteration budget under the algorithm's chosen params key
        (`'iterations'` or `'generations'`), and the problem-type code.
        """
        from problems import prob_type_of
        self.problem      = problem
        self.params       = params
        self.maximize     = maximize
        self.current_iter = 0
        self.max_iters    = params[iters_key]
        self._prob_type   = prob_type_of(problem)

    @property
    def is_finished(self) -> bool:
        return self.current_iter >= self.max_iters

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
