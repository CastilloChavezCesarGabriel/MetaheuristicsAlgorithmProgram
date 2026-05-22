"""
Correctness suite — 40 tests, 8 properties × 5 algorithms.

Every test answers: given THESE inputs, does the algorithm produce the
result it SHOULD? Loose tolerances are used because metaheuristics are
stochastic, but every assertion is a behavioral claim (not just "ran
without errors").

Properties verified per algorithm:
    A. Continuous minimization converges near the known minimum
    B. Continuous maximization converges near the known maximum
    C. Knapsack maximization reaches near-optimal value
    D. TSP minimization finds a short tour
    E. Categorical minimization picks the right category
    F. Knapsack solutions are binary (constraint validity)
    G. best_so_far is monotonic (never gets worse)
    H. max and min runs produce meaningfully different fitness

Run:   python3 -m pytest tests/test_correctness.py -v
"""
import queue
import threading

import numpy as np
import pytest
import sys
sys.path.insert(0, '.')

from engine.runner       import Runner
from algorithms          import ALGORITHM_CLASSES
from problems.continuous  import ContinuousProblem
from problems.knapsack    import KnapsackProblem
from problems.categorical import CategoricalProblem
from problems.tsp         import TspProblem


ALGO_CODES = ['ga', 'pso', 'aco', 'ais', 'de']


# ---------------------------------------------------------------------------
# Param recipes — tuned to give each algorithm a fair shot at convergence
# ---------------------------------------------------------------------------

def params_for(algo, prob_type):
    if algo == 'ga':
        return {'population_size': 30, 'generations': 80,
                'crossover_rate': 0.85, 'mutation_rate': 0.1,
                'tournament_size': 3,   'blx_alpha': 0.5}
    if algo == 'pso':
        return {'num_particles': 30, 'iterations': 80,
                'w': 0.7, 'c1': 1.5, 'c2': 1.5, 'vmax': 5.0}
    if algo == 'aco':
        if prob_type in ('continuous', 'categorical'):
            return {'num_ants': 20, 'iterations': 80,
                    'k': 10, 'q': 0.05, 'xi': 0.85}
        return {'num_ants': 20, 'iterations': 80,
                'alpha': 1.0, 'beta': 3.0, 'rho': 0.1,
                'Q': 100.0, 'tau0': 0.1}
    if algo == 'ais':
        return {'population_size': 30, 'generations': 80,
                'beta': 1.0, 'd': 0.1, 'rho': 3.0}
    return {'population_size': 30, 'generations': 80,
            'F': 0.8, 'CR': 0.9, 'strategy': 'DE/rand/1'}


def run_to_completion(algo, problem, params, maximize, timeout=30):
    """Run one experiment with convergence disabled (high patience)."""
    runner = Runner(problem, ALGORITHM_CLASSES[algo](), params, maximize,
                    convergence_patience=10_000)
    q = queue.Queue()
    cancel = threading.Event()
    runner.start(q, cancel)
    while True:
        msg = q.get(timeout=timeout)
        if msg['type'] == 'done':
            return msg['history']
        if msg['type'] == 'error':
            raise RuntimeError(f"{algo} runner error: {msg['message']}")


@pytest.fixture(autouse=True)
def _deterministic_seed():
    """Each test starts from the same numpy seed for reproducibility."""
    np.random.seed(42)
    yield


# ─────────────────────────────────────────────────────────────────────────────
# A. Continuous minimization
#    f(x) = x²  on [-5, 5].  Global minimum: x=0, f=0.
#    Claim: every algorithm reaches |x|<1 and f<1.
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize('algo', ALGO_CODES)
def test_A_continuous_min_x_squared(algo):
    problem = ContinuousProblem('x1**2', 1, [(-5.0, 5.0)])
    h = run_to_completion(algo, problem, params_for(algo, 'continuous'),
                          maximize=False)
    assert h.best_fx < 1.0, \
        f'{algo} failed to minimize x²: best_fx={h.best_fx:.4f} (expected <1)'
    assert abs(h.best_solution[0]) < 1.0, \
        f'{algo} x far from 0: x={h.best_solution[0]:.4f}'


# ─────────────────────────────────────────────────────────────────────────────
# B. Continuous maximization
#    f(x) = -(x-2)²  on [-5, 5].  Maximum: x=2, f=0.
#    Claim: every algorithm reaches x≈2 and f>-1.
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize('algo', ALGO_CODES)
def test_B_continuous_max_shifted_parabola(algo):
    problem = ContinuousProblem('-(x1 - 2)**2', 1, [(-5.0, 5.0)])
    h = run_to_completion(algo, problem, params_for(algo, 'continuous'),
                          maximize=True)
    assert h.best_fx > -1.0, \
        f'{algo} failed to maximize -(x-2)²: best_fx={h.best_fx:.4f}'
    assert abs(h.best_solution[0] - 2.0) < 1.0, \
        f'{algo} x far from 2: x={h.best_solution[0]:.4f}'


# ─────────────────────────────────────────────────────────────────────────────
# C. Knapsack maximization
#    5 items, weights [2,3,4,5,9], values [3,4,5,8,10], W=10, alpha=10.
#    Brute-force optimum: items {0,1,3} → weight 10, value 15.
#    Claim: every algorithm reaches a value ≥ 11 (within ~75% of optimal).
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize('algo', ALGO_CODES)
def test_C_knapsack_max_reaches_near_optimum(algo):
    problem = KnapsackProblem(5, [2, 3, 4, 5, 9], [3, 4, 5, 8, 10],
                              W=10, alpha=10)
    h = run_to_completion(algo, problem, params_for(algo, 'knapsack'),
                          maximize=True)
    assert h.best_fx >= 11.0, \
        f'{algo} knapsack value {h.best_fx:.2f} below threshold (optimum=15)'


# ─────────────────────────────────────────────────────────────────────────────
# D. TSP minimization
#    5 cities forming a 100×100 square + center at (50,50).
#    Reasonable tours are 400-500. Worst-case ≈ 600+.
#    Claim: every algorithm finds a tour ≤ 500.
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize('algo', ALGO_CODES)
def test_D_tsp_min_finds_short_tour(algo):
    problem = TspProblem(5, [(0, 0), (100, 0), (100, 100),
                              (0, 100), (50, 50)])
    h = run_to_completion(algo, problem, params_for(algo, 'tsp'),
                          maximize=False)
    assert h.best_fx <= 500.0, \
        f'{algo} TSP tour distance {h.best_fx:.2f} > 500'


# ─────────────────────────────────────────────────────────────────────────────
# E. Categorical minimization
#    f(x,D) = x² + D, x∈[-5,5], D ∈ {-3, -1, 7, -9}.
#    Minimum: x=0, category=3 (D=-9) → f=-9.
#    Claim: every algorithm reaches f < -6 (i.e. picks the -9 category).
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize('algo', ALGO_CODES)
def test_E_categorical_min_picks_best_category(algo):
    problem = CategoricalProblem('x1**2 + D', 1, [(-5.0, 5.0)],
                                 num_options=4,
                                 option_values=[-3, -1, 7, -9])
    h = run_to_completion(algo, problem, params_for(algo, 'categorical'),
                          maximize=False)
    assert h.best_fx < -6.0, \
        f'{algo} categorical f={h.best_fx:.2f}, expected to find D=-9 category'


# ─────────────────────────────────────────────────────────────────────────────
# F. Constraint validity — knapsack solutions must be 0/1
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize('algo', ALGO_CODES)
def test_F_knapsack_solution_is_binary(algo):
    problem = KnapsackProblem(5, [2, 3, 4, 5, 9], [3, 4, 5, 8, 10],
                              W=10, alpha=10)
    h = run_to_completion(algo, problem, params_for(algo, 'knapsack'),
                          maximize=True)
    for i, v in enumerate(h.best_solution):
        assert round(float(v)) in (0, 1), \
            f'{algo} knapsack solution[{i}] = {v} (not 0/1)'


# ─────────────────────────────────────────────────────────────────────────────
# G. Monotonicity — best_so_far series never decreases (fitness terms)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize('algo', ALGO_CODES)
def test_G_best_so_far_is_monotonic(algo):
    problem = ContinuousProblem('x1**2', 1, [(-5.0, 5.0)])
    h = run_to_completion(algo, problem, params_for(algo, 'continuous'),
                          maximize=False)
    bsf = h._best_so_far
    for i in range(1, len(bsf)):
        assert bsf[i] >= bsf[i - 1] - 1e-9, \
            (f'{algo} best_so_far dropped at iter {i}: '
             f'{bsf[i-1]:.6f} → {bsf[i]:.6f}')


# ─────────────────────────────────────────────────────────────────────────────
# H. Maximize and minimize produce meaningfully different fitness on the
#    same problem.
#    f(x) = -(x-2)²  on [-5, 5].  Max: f=0 at x=2.  Min: f=-25 at x=-3.
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize('algo', ALGO_CODES)
def test_H_max_and_min_yield_different_results(algo):
    problem = ContinuousProblem('-(x1 - 2)**2', 1, [(-5.0, 5.0)])

    np.random.seed(42)
    h_max = run_to_completion(algo, problem, params_for(algo, 'continuous'),
                              maximize=True)

    np.random.seed(43)
    h_min = run_to_completion(algo, problem, params_for(algo, 'continuous'),
                              maximize=False)

    # f(max) should be at least 5 units above f(min)
    assert h_max.best_fx > h_min.best_fx + 5.0, \
        (f'{algo} max and min indistinguishable: '
         f'max f={h_max.best_fx:.2f}, min f={h_min.best_fx:.2f}')
