class RunHistory:
    """Acumula el historial de fitness por iteración y lo segmenta
    en las 4 ventanas requeridas por la pantalla de resultados (sección 5.1)."""

    def __init__(self, total_iterations: int):
        self._total_iterations = total_iterations
        self._iterations: list[int] = []
        self._best_fitness: list[float] = []
        self._avg_fitness: list[float] = []
        self._best_so_far: list[float] = []
        self._best_overall_fitness: float = float('-inf')
        self._best_overall_fx: float = float('nan')
        self._best_overall_solution = None
        self._best_overall_iteration: int = 0

    def record(self, iteration: int, best_fitness: float, avg_fitness: float,
               best_solution, fx: float):
        self._iterations.append(iteration)
        self._best_fitness.append(best_fitness)
        self._avg_fitness.append(avg_fitness)

        running_best = (
            max(self._best_so_far[-1], best_fitness)
            if self._best_so_far
            else best_fitness
        )
        self._best_so_far.append(running_best)

        if best_fitness > self._best_overall_fitness:
            self._best_overall_fitness = best_fitness
            self._best_overall_fx = fx
            self._best_overall_solution = best_solution
            self._best_overall_iteration = iteration

    @property
    def best_fitness(self) -> float:
        return self._best_overall_fitness

    @property
    def best_fx(self) -> float:
        return self._best_overall_fx

    @property
    def best_solution(self):
        return self._best_overall_solution

    @property
    def best_iteration(self) -> int:
        return self._best_overall_iteration

    @property
    def total_recorded(self) -> int:
        return len(self._iterations)

    def get_segments(self) -> list[dict]:
        """Retorna 4 segmentos de datos para las gráficas (sección 5.1)."""
        t = self._total_iterations
        t1 = t // 3
        t2 = 2 * t // 3

        def _slice(lo, hi):
            idx = [i for i, it in enumerate(self._iterations) if lo < it <= hi]
            return {
                'iterations': [self._iterations[i] for i in idx],
                'best_so_far': [self._best_so_far[i] for i in idx],
                'avg_fitness': [self._avg_fitness[i] for i in idx],
            }

        return [
            {**_slice(0, t1),  'title': f'Fase de Exploracion (0 - 1/3)'},
            {**_slice(t1, t2), 'title': f'Fase de Transicion (1/3 - 2/3)'},
            {**_slice(t2, t),  'title': f'Fase de Refinamiento (2/3 - 3/3)'},
            {**_slice(0, t),   'title': f'Convergencia Global (0 - {t})'},
        ]
