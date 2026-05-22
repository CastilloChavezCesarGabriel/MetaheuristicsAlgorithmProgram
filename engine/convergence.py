def default_patience(total_iterations: int) -> int:
    """N por defecto: 10% del total, mínimo 5 (sección 6)."""
    return max(5, round(total_iterations * 0.1))


class ConvergenceChecker:
    """Detecta convergencia anticipada cuando el mejor fitness no mejora
    en las últimas N iteraciones consecutivas (sección 6)."""

    def __init__(self, patience: int, epsilon: float = 1e-10):
        self.patience = patience
        self.epsilon = epsilon
        self._history: list[float] = []

    def check(self, best_fitness: float) -> bool:
        """Registra best_fitness y retorna True si convergió."""
        self._history.append(best_fitness)
        if len(self._history) < self.patience:
            return False
        reference = self._history[-self.patience]
        return abs(best_fitness - reference) < self.epsilon

    def reset(self):
        self._history.clear()
