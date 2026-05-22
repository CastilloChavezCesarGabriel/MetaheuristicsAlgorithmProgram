import numpy as np

from algorithms.base_algorithm import BaseAlgorithm
from problems.base_problem import calculate_fitness


def _eval_de(problem, ind, maximize, prob_type):
    if prob_type == 'tsp':
        route = np.argsort(ind).astype(float)
        fx = problem.evaluate(route)
    elif prob_type == 'knapsack':
        binary = (ind >= 0.5).astype(float)
        fx = problem.evaluate(binary)
    else:
        fx = problem.evaluate(ind)
    return calculate_fitness(fx, maximize)


def _best_solution_de(ind, prob_type):
    if prob_type == 'tsp':
        return np.argsort(ind).astype(float)
    if prob_type == 'knapsack':
        return (ind >= 0.5).astype(float)
    return ind.copy()


class DifferentialEvolution(BaseAlgorithm):

    def initialize(self, problem, params: dict, maximize: bool):
        self._prepare(problem, params, maximize, iters_key='generations')

        pop_size = params['population_size']

        if self._prob_type == 'tsp':
            self._lb = np.zeros(problem.n)
            self._ub = np.ones(problem.n)
            self.pop = np.random.uniform(0, 1, (pop_size, problem.n))
        elif self._prob_type == 'knapsack':
            self._lb = np.zeros(problem.n)
            self._ub = np.ones(problem.n)
            self.pop = np.random.uniform(0, 1, (pop_size, problem.n))
        else:
            bounds = np.array(problem.bounds)
            self._lb = bounds[:, 0]
            self._ub = bounds[:, 1]
            self.pop = np.array([problem.generate_random_solution() for _ in range(pop_size)])
            self.pop = np.clip(self.pop, self._lb, self._ub)

        self.pop_fit = np.array([
            _eval_de(problem, ind, maximize, self._prob_type)
            for ind in self.pop
        ])

    def step(self) -> dict:
        F  = self.params['F']
        CR = self.params['CR']
        pop_size = len(self.pop)
        dim = self.pop.shape[1]
        new_pop = self.pop.copy()
        new_fit = self.pop_fit.copy()

        for i in range(pop_size):
            # Select 3 distinct individuals ≠ i
            candidates = [j for j in range(pop_size) if j != i]
            a_idx, b_idx, c_idx = np.random.choice(candidates, 3, replace=False)
            a, b, c = self.pop[a_idx], self.pop[b_idx], self.pop[c_idx]

            # Mutant DE/rand/1
            mutant = a + F * (b - c)
            mutant = np.clip(mutant, self._lb, self._ub)

            # Binomial crossover
            mask = np.random.random(dim) < CR
            mask[np.random.randint(dim)] = True
            trial = np.where(mask, mutant, self.pop[i])

            # Greedy selection
            trial_fit = _eval_de(self.problem, trial, self.maximize, self._prob_type)
            if trial_fit >= self.pop_fit[i]:
                new_pop[i] = trial
                new_fit[i] = trial_fit

        self.pop     = new_pop
        self.pop_fit = new_fit
        self.current_iter += 1

        best_idx = int(np.argmax(self.pop_fit))
        best_sol = _best_solution_de(self.pop[best_idx], self._prob_type)

        return {
            'best_fitness':  float(self.pop_fit[best_idx]),
            'avg_fitness':   float(np.mean(self.pop_fit)),
            'best_solution': best_sol,
            'iteration':     self.current_iter,
        }

    def get_param_schema(self, problem_type: str) -> list[dict]:
        return [
            {'name': 'population_size', 'type': 'int',   'min': 4,   'max': 1000, 'default': 50,
             'description': 'Tamano de la poblacion'},
            {'name': 'generations',     'type': 'int',   'min': 10,  'max': 10000,'default': 100,
             'description': 'Numero de generaciones'},
            {'name': 'F',               'type': 'float', 'min': 0.01,'max': 2.0,  'default': 0.8,
             'description': 'Factor de escala F'},
            {'name': 'CR',              'type': 'float', 'min': 0.0, 'max': 1.0,  'default': 0.9,
             'description': 'Tasa de cruza CR'},
            {'name': 'strategy',        'type': 'str',                'default': 'DE/rand/1',
             'description': 'Estrategia de mutacion'},
        ]
