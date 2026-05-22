import queue
import threading
import time

from engine.convergence import ConvergenceChecker, default_patience
from engine.history import RunHistory
from problems.base_problem import calculate_fitness


class Runner:
    """Orquesta la ejecución de un algoritmo sobre un problema en un thread
    separado, comunicándose con la GUI vía queue.Queue (sección 12).

    `step_delay` (seconds) pauses the loop after each iteration. Used for
    TSP animation: 0.05s gives ~20 fps so the user can actually see the
    tour evolve frame by frame instead of finishing in a 1-second blur.
    """

    def __init__(self, problem, algorithm, params: dict, maximize: bool,
                 convergence_patience: int = None, step_delay: float = 0.0):
        self._problem = problem
        self._algorithm = algorithm
        self._params = params
        self._maximize = maximize
        self._step_delay = max(0.0, float(step_delay))

        self._total_iterations = (
            params.get('generations') or params.get('iterations') or 100
        )

        patience = (
            convergence_patience
            if convergence_patience is not None
            else default_patience(self._total_iterations)
        )
        self._convergence = ConvergenceChecker(patience)
        self._history = RunHistory(self._total_iterations)

    def start(self, result_queue: queue.Queue,
              cancel_event: threading.Event) -> threading.Thread:
        t = threading.Thread(
            target=self._run,
            args=(result_queue, cancel_event),
            daemon=True,
        )
        t.start()
        return t

    def _run(self, result_queue: queue.Queue, cancel_event: threading.Event):
        converged = False
        try:
            self._algorithm.initialize(
                self._problem, self._params, self._maximize
            )

            while (not self._algorithm.is_finished
                   and not cancel_event.is_set()):

                step_result = self._algorithm.step()
                fx = self._problem.evaluate(step_result['best_solution'])

                self._history.record(
                    iteration=step_result['iteration'],
                    best_fitness=step_result['best_fitness'],
                    avg_fitness=step_result['avg_fitness'],
                    best_solution=step_result['best_solution'],
                    fx=fx,
                )

                progress_msg = {
                    'type': 'progress',
                    'iteration': step_result['iteration'],
                    'total': self._total_iterations,
                    'best_fitness': step_result['best_fitness'],
                    'avg_fitness': step_result['avg_fitness'],
                    'best_solution': step_result.get('best_solution'),
                }
                result_queue.put(progress_msg)

                if self._convergence.check(step_result['best_fitness']):
                    converged = True
                    break

                if self._step_delay > 0.0 and not cancel_event.is_set():
                    # interruptible sleep so Cancelar stays responsive
                    cancel_event.wait(self._step_delay)

        except Exception as exc:
            result_queue.put({'type': 'error', 'message': str(exc)})
            return

        result_queue.put({
            'type': 'done',
            'history': self._history,
            'converged': converged,
            'cancelled': cancel_event.is_set(),
        })
