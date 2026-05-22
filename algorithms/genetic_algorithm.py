import numpy as np

from algorithms.base_algorithm import BaseAlgorithm
from problems.base_problem import calculate_fitness


# ── Continuous operators ──────────────────────────────────────────────────────

def _tournament_select(population, fitnesses, k):
    indices = np.random.choice(len(population), size=k, replace=False)
    best = max(indices, key=lambda i: fitnesses[i])
    return population[best].copy()


def _blx_alpha_crossover(p1, p2, alpha, bounds, rate):
    if np.random.random() >= rate:
        return p1.copy(), p2.copy()
    c1 = np.empty(len(p1))
    c2 = np.empty(len(p1))
    for i in range(len(p1)):
        lo, hi = min(p1[i], p2[i]), max(p1[i], p2[i])
        interval = hi - lo
        lb = max(lo - alpha * interval, bounds[i][0])
        ub = min(hi + alpha * interval, bounds[i][1])
        c1[i] = np.random.uniform(lb, ub)
        c2[i] = np.random.uniform(lb, ub)
    return c1, c2


def _gaussian_mutation(individual, rate, bounds):
    mutant = individual.copy()
    for i in range(len(mutant)):
        if np.random.random() < rate:
            sigma = 0.1 * (bounds[i][1] - bounds[i][0])
            mutant[i] += np.random.normal(0, sigma)
            mutant[i] = np.clip(mutant[i], bounds[i][0], bounds[i][1])
    return mutant


# ── Binary operators (Knapsack) ───────────────────────────────────────────────

def _one_point_crossover(p1, p2, rate):
    if np.random.random() >= rate:
        return p1.copy(), p2.copy()
    pt = np.random.randint(1, len(p1))
    return (np.concatenate([p1[:pt], p2[pt:]]),
            np.concatenate([p2[:pt], p1[pt:]]))


def _bit_flip_mutation(ind, rate):
    child = ind.copy()
    mask = np.random.random(len(child)) < rate
    child[mask] = 1.0 - child[mask]
    return child


# ── Permutation operators (TSP) ───────────────────────────────────────────────

def _ox_crossover(p1, p2):
    n = len(p1)
    p1i = p1.astype(int)
    p2i = p2.astype(int)
    a, b = sorted(np.random.choice(n, 2, replace=False))
    child = np.full(n, -1, dtype=int)
    child[a:b + 1] = p1i[a:b + 1]
    rem = [x for x in p2i if x not in child]
    pos = 0
    for k in range(n):
        if child[k] == -1:
            child[k] = rem[pos]
            pos += 1
    return child.astype(float)


def _swap_mutation(ind, rate):
    child = ind.copy()
    if np.random.random() < rate:
        i, j = np.random.choice(len(child), 2, replace=False)
        child[i], child[j] = child[j], child[i]
    return child


# ── GeneticAlgorithm ──────────────────────────────────────────────────────────

class GeneticAlgorithm(BaseAlgorithm):

    def initialize(self, problem, params: dict, maximize: bool):
        self._prepare(problem, params, maximize, iters_key='generations')

        pop_size = params['population_size']
        self.population = [problem.generate_random_solution() for _ in range(pop_size)]

    def _crossover(self, p1, p2):
        rate = self.params['crossover_rate']
        if self._prob_type == 'knapsack':
            return _one_point_crossover(p1, p2, rate)
        if self._prob_type == 'tsp':
            if np.random.random() < rate:
                return _ox_crossover(p1, p2), _ox_crossover(p2, p1)
            return p1.copy(), p2.copy()
        # continuous and categorical: BLX-alpha on full vector
        alpha = self.params.get('blx_alpha', 0.5)
        bounds = self.problem.bounds
        return _blx_alpha_crossover(p1, p2, alpha, bounds, rate)

    def _mutate(self, ind):
        rate = self.params['mutation_rate']
        if self._prob_type == 'knapsack':
            return _bit_flip_mutation(ind, rate)
        if self._prob_type == 'tsp':
            return _swap_mutation(ind, rate)
        if self._prob_type == 'categorical':
            # Gaussian for continuous dims; random replacement for category index
            bounds = self.problem.bounds
            child = _gaussian_mutation(ind.copy(), rate, bounds)
            if np.random.random() < rate:
                child[-1] = float(np.random.randint(0, self.problem.num_options))
            return child
        return _gaussian_mutation(ind, rate, self.problem.bounds)

    def step(self) -> dict:
        pop_size = self.params['population_size']
        tournament_size = self.params['tournament_size']

        fitnesses = [
            calculate_fitness(self.problem.evaluate(ind), self.maximize)
            for ind in self.population
        ]

        new_population = []
        while len(new_population) < pop_size:
            p1 = _tournament_select(self.population, fitnesses, tournament_size)
            p2 = _tournament_select(self.population, fitnesses, tournament_size)
            c1, c2 = self._crossover(p1, p2)
            new_population.append(self._mutate(c1))
            if len(new_population) < pop_size:
                new_population.append(self._mutate(c2))

        self.population = new_population
        self.current_iter += 1

        fitnesses = [
            calculate_fitness(self.problem.evaluate(ind), self.maximize)
            for ind in self.population
        ]
        best_idx = int(np.argmax(fitnesses))

        return {
            'best_fitness':  fitnesses[best_idx],
            'avg_fitness':   float(np.mean(fitnesses)),
            'best_solution': self.population[best_idx].copy(),
            'iteration':     self.current_iter,
        }

    def get_param_schema(self, problem_type: str) -> list[dict]:
        base = [
            {'name': 'population_size', 'type': 'int',   'min': 4,   'max': 1000,  'default': 50,
             'description': 'Tamano de la poblacion'},
            {'name': 'generations',     'type': 'int',   'min': 10,  'max': 10000, 'default': 100,
             'description': 'Numero de generaciones'},
            {'name': 'crossover_rate',  'type': 'float', 'min': 0.0, 'max': 1.0,   'default': 0.8,
             'description': 'Tasa de cruza'},
            {'name': 'mutation_rate',   'type': 'float', 'min': 0.0, 'max': 1.0,   'default': 0.1,
             'description': 'Tasa de mutacion'},
            {'name': 'tournament_size', 'type': 'int',   'min': 2,   'max': 20,    'default': 3,
             'description': 'Tamano del torneo'},
        ]
        if problem_type in ('continuous', 'categorical'):
            base.append({
                'name': 'blx_alpha', 'type': 'float', 'min': 0.0, 'max': 2.0, 'default': 0.5,
                'description': 'Parametro alpha del BLX-alpha',
            })
        return base
