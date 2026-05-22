from abc import ABC, abstractmethod


def calculate_fitness(fx: float, maximize: bool) -> float:
    """Único punto de transformación f(x) → fitness (sección 7 del spec)."""
    if maximize:
        return fx
    return -fx


class BaseProblem(ABC):

    @abstractmethod
    def evaluate(self, solution) -> float:
        """Evalúa el fitness de una solución."""
        pass

    @abstractmethod
    def generate_random_solution(self):
        """Genera una solución aleatoria válida."""
        pass

    @abstractmethod
    def get_param_schema(self) -> list[dict]:
        """Retorna la lista de parámetros configurables del problema.
        Cada dict: {name, type, min, max, default, description}"""
        pass

    @abstractmethod
    def validate_solution(self, solution) -> bool:
        """Valida si una solución es válida para este problema."""
        pass
