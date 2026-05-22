import numpy as np

from algorithms.base_algorithm import BaseAlgorithm
from problems.base_problem import calculate_fitness


class AIS(BaseAlgorithm):

    def initialize(self, problem, params: dict, maximize: bool):
        from problems import prob_type_of

        self.problem  = problem
        self.params   = params
        self.maximize = maximize
        self.current_iter = 0
        self.max_iters = params['generations']

        self._prob_type = prob_type_of(problem)

        pop_size = params['population_size']
        self.pop = [problem.generate_random_solution() for _ in range(pop_size)]
        self.pop_fit = [
            calculate_fitness(problem.evaluate(s), maximize)
            for s in self.pop
        ]

    def _hypermutate(self, ab, fit):
        rho = self.params['rho']
        # Affinity-proportional: higher |fit| = less mutation (exploit best clones)
        sigma = rho / (1.0 + max(abs(fit), 1e-10))
        sigma = min(sigma, 2.0)

        if self._prob_type == 'continuous':
            return self._gaussian_bounded(ab, sigma)

        if self._prob_type == 'knapsack':
            rate = min(0.9, sigma * 0.3)
            child = ab.copy()
            mask = np.random.random(len(child)) < rate
            child[mask] = 1.0 - child[mask]
            return child

        if self._prob_type == 'categorical':
            bounds = self.problem._cont_bounds
            child  = self._gaussian_bounded_partial(ab[:-1], sigma, bounds)
            if np.random.random() < sigma * 0.5:
                cat = float(np.random.randint(0, self.problem.num_options))
            else:
                cat = ab[-1]
            return np.append(child, cat)

        # TSP: swap-based
        n_swaps = max(1, int(sigma * self.problem.n * 0.2))
        child = ab.copy()
        for _ in range(n_swaps):
            i, j = np.random.choice(self.problem.n, 2, replace=False)
            child[i], child[j] = child[j], child[i]
        return child

    def _gaussian_bounded(self, ab, sigma):
        bounds = self.problem.bounds
        child  = ab.copy()
        for i, (lb, ub) in enumerate(bounds):
            child[i] += np.random.normal(0, sigma * max(ub - lb, 1e-6) * 0.1)
            child[i]  = np.clip(child[i], lb, ub)
        return child

    def _gaussian_bounded_partial(self, ab, sigma, bounds):
        child = ab.copy()
        for i, (lb, ub) in enumerate(bounds):
            child[i] += np.random.normal(0, sigma * max(ub - lb, 1e-6) * 0.1)
            child[i]  = np.clip(child[i], lb, ub)
        return child

    def step(self) -> dict:
        beta  = self.params['beta']
        d     = self.params['d']
        pop_size = len(self.pop)

        # 1. Sort by fitness (descending)
        order = np.argsort(self.pop_fit)[::-1]

        # 2. Clone top n_select antibodies
        n_select = max(1, round(beta * pop_size))
        all_clones = []
        all_clone_fits = []

        for rank, idx in enumerate(order[:n_select]):
            ab  = self.pop[idx]
            fit = self.pop_fit[idx]
            n_clones = max(1, round(beta * pop_size / (rank + 1)))
            for _ in range(n_clones):
                clone = self._hypermutate(ab, fit)
                clone_fit = calculate_fitness(
                    self.problem.evaluate(clone), self.maximize)
                all_clones.append(clone)
                all_clone_fits.append(clone_fit)

        # 3. Select best clone for each selected antibody and replace if better
        pos = 0
        for rank, idx in enumerate(order[:n_select]):
            n_clones = max(1, round(beta * pop_size / (rank + 1)))
            segment_fits = all_clone_fits[pos:pos + n_clones]
            best_clone_idx = pos + int(np.argmax(segment_fits))
            if all_clone_fits[best_clone_idx] > self.pop_fit[idx]:
                self.pop[idx]     = all_clones[best_clone_idx]
                self.pop_fit[idx] = all_clone_fits[best_clone_idx]
            pos += n_clones

        # 4. Replace d fraction of worst with new random antibodies
        n_replace = max(1, round(d * pop_size))
        worst_idx = np.argsort(self.pop_fit)[:n_replace]
        for i in worst_idx:
            new_ab = self.problem.generate_random_solution()
            self.pop[i]     = new_ab
            self.pop_fit[i] = calculate_fitness(
                self.problem.evaluate(new_ab), self.maximize)

        self.current_iter += 1

        best_idx = int(np.argmax(self.pop_fit))
        return {
            'best_fitness':  float(self.pop_fit[best_idx]),
            'avg_fitness':   float(np.mean(self.pop_fit)),
            'best_solution': self.pop[best_idx].copy(),
            'iteration':     self.current_iter,
        }

    def get_param_schema(self, problem_type: str) -> list[dict]:
        return [
            {'name': 'population_size', 'type': 'int',   'min': 4,   'max': 500, 'default': 30,
             'description': 'Tamano de la poblacion (anticuerpos)'},
            {'name': 'generations',     'type': 'int',   'min': 10,  'max': 10000,'default': 100,
             'description': 'Numero de generaciones'},
            {'name': 'beta',            'type': 'float', 'min': 0.01,'max': 5.0, 'default': 1.0,
             'description': 'Factor de clonacion beta'},
            {'name': 'd',               'type': 'float', 'min': 0.01,'max': 0.99,'default': 0.1,
             'description': 'Tasa de reemplazo d'},
            {'name': 'rho',             'type': 'float', 'min': 0.01,'max': 10.0,'default': 3.0,
             'description': 'Parametro de decaimiento rho'},
        ]

    @property
    def is_finished(self) -> bool:
        return self.current_iter >= self.max_iters
