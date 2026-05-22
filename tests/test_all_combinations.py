"""
Fase 9 — Testing de las 20 combinaciones.
Prueba el pipeline completo: Runner -> hilo -> queue -> RunHistory -> done/error.
Uso: python tests/test_all_combinations.py
"""
import queue
import sys
import threading
import traceback

sys.path.insert(0, '.')

from engine.runner import Runner
from problems.continuous   import ContinuousProblem
from problems.knapsack     import KnapsackProblem
from problems.categorical  import CategoricalProblem
from problems.tsp          import TspProblem
from algorithms.genetic_algorithm       import GeneticAlgorithm
from algorithms.pso                     import PSO
from algorithms.aco                     import ACO
from algorithms.ais                     import AIS
from algorithms.differential_evolution  import DifferentialEvolution

# ---------------------------------------------------------------------------
# Parámetros mínimos (30 iters para que los 4 segmentos tengan datos)
# ---------------------------------------------------------------------------

PARAMS_GA = {
    'population_size': 10, 'generations': 30,
    'crossover_rate': 0.8, 'mutation_rate': 0.1,
    'tournament_size': 2,  'blx_alpha': 0.5,
}
PARAMS_PSO = {
    'num_particles': 8, 'iterations': 30,
    'w': 0.7, 'c1': 1.5, 'c2': 1.5, 'vmax': 5.0,
}
PARAMS_ACO_CR = {   # continua / categórica
    'num_ants': 5, 'iterations': 30, 'k': 5, 'q': 0.01, 'xi': 0.85,
}
PARAMS_ACO_KN = {   # knapsack / tsp
    'num_ants': 5, 'iterations': 30, 'alpha': 1.0, 'beta': 2.0,
    'rho': 0.1, 'Q': 10.0, 'tau0': 0.1,
}
PARAMS_AIS = {
    'population_size': 10, 'generations': 30,
    'beta': 1.0, 'd': 0.1, 'rho': 3.0,
}
PARAMS_DE = {
    'population_size': 10, 'generations': 30,
    'F': 0.8, 'CR': 0.9, 'strategy': 'DE/rand/1',
}

PROBLEMS = {
    'continuous':  ContinuousProblem('x1**2', 1, [(-5.0, 5.0)]),
    'knapsack':    KnapsackProblem(5, [2, 3, 1, 4, 2], [3, 4, 1, 5, 2], 7, 10),
    'categorical': CategoricalProblem('x1**2+D', 1, [(-5, 5)], 4, [-3, -1, 7, -9]),
    'tsp':         TspProblem(5, [(0, 0), (100, 0), (100, 100), (0, 100), (50, 50)]),
}

ALGO_CLASSES = {
    'ga':  GeneticAlgorithm,
    'pso': PSO,
    'aco': ACO,
    'ais': AIS,
    'de':  DifferentialEvolution,
}


def _get_params(algo: str, prob: str) -> dict:
    if algo == 'ga':
        return PARAMS_GA.copy()
    if algo == 'pso':
        return PARAMS_PSO.copy()
    if algo == 'aco':
        return PARAMS_ACO_CR.copy() if prob in ('continuous', 'categorical') else PARAMS_ACO_KN.copy()
    if algo == 'ais':
        return PARAMS_AIS.copy()
    return PARAMS_DE.copy()


def _run_one(prob_name: str, algo_name: str, maximize: bool) -> tuple[bool, str]:
    """Corre el pipeline completo para una combinación. Retorna (ok, detalle)."""
    try:
        problem   = PROBLEMS[prob_name]
        algorithm = ALGO_CLASSES[algo_name]()
        params    = _get_params(algo_name, prob_name)
        patience  = 5

        runner = Runner(problem, algorithm, params, maximize, patience)
        q      = queue.Queue()
        cancel = threading.Event()
        runner.start(q, cancel)

        # Drenar la cola hasta recibir done/error (timeout 30 s)
        history = None
        while True:
            try:
                msg = q.get(timeout=30)
            except queue.Empty:
                return False, 'Timeout: el hilo no terminó en 30 s'

            if msg['type'] == 'error':
                return False, f"Runner error: {msg.get('message', '?')}"
            if msg['type'] == 'done':
                history = msg['history']
                break
            # 'progress' — continuar drenando

        # --- Verificaciones ---
        if history.total_recorded < 1:
            return False, 'history.total_recorded == 0'

        bsf = history._best_so_far
        for i in range(len(bsf) - 1):
            if bsf[i] > bsf[i + 1] + 1e-12:
                return False, f'best_so_far no monotonico en iter {i}: {bsf[i]:.6f} > {bsf[i+1]:.6f}'

        segs = history.get_segments()
        if len(segs) != 4:
            return False, f'get_segments() retornó {len(segs)} segmentos, esperados 4'

        if history.best_solution is None:
            return False, 'best_solution es None'

        return True, f'iters={history.total_recorded}  best_fx={history.best_fx:.4f}'

    except Exception:
        return False, traceback.format_exc()


def main():
    problems   = ['continuous', 'knapsack', 'categorical', 'tsp']
    algorithms = ['ga', 'pso', 'aco', 'ais', 'de']

    passed = 0
    failed = 0

    for prob in problems:
        for algo in algorithms:
            ok, detail = _run_one(prob, algo, maximize=False)
            status = 'OK  ' if ok else 'FAIL'
            label  = f'{prob:<12} x {algo:<4}'
            print(f'{label}  {status}  {detail}')
            if ok:
                passed += 1
            else:
                failed += 1

    print()
    total = passed + failed
    if failed == 0:
        print(f'FASE 9: {passed}/{total} combinaciones OK')
    else:
        print(f'FASE 9: {passed}/{total} OK  |  {failed} FALLARON')
        sys.exit(1)


if __name__ == '__main__':
    main()
