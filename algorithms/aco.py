import numpy as np

from algorithms.base_algorithm import BaseAlgorithm
from problems.base_problem import calculate_fitness


def _gaussian_weights(k, q):
    ranks = np.arange(1, k + 1, dtype=float)
    w = np.exp(-((ranks - 1) ** 2) / (2 * q ** 2 * k ** 2))
    w /= w.sum()
    return w


class ACO(BaseAlgorithm):

    def initialize(self, problem, params: dict, maximize: bool):
        self._prepare(problem, params, maximize, iters_key='iterations')
        self.num_ants = params['num_ants']

        if self._prob_type in ('continuous', 'categorical'):
            self._init_acor()
        elif self._prob_type == 'knapsack':
            self._init_aco_knapsack()
        else:
            self._init_aco_tsp()

        # Track global best
        self._best_solution = None
        self._best_fitness  = -np.inf

    # ── ACO-R (Continuous / Categorical) ─────────────────────────────────────

    def _init_acor(self):
        k = self.params['k']
        self._archive = [self.problem.generate_random_solution() for _ in range(k)]
        self._archive_fit = [
            calculate_fitness(self.problem.evaluate(s), self.maximize)
            for s in self._archive
        ]
        self._sort_archive()

    def _sort_archive(self):
        order = np.argsort(self._archive_fit)[::-1]
        self._archive     = [self._archive[i] for i in order]
        self._archive_fit = [self._archive_fit[i] for i in order]

    def _step_acor(self) -> dict:
        k   = self.params['k']
        q   = self.params['q']
        xi  = self.params['xi']
        weights = _gaussian_weights(k, q)
        dim = len(self._archive[0])
        archive_arr = np.array(self._archive)

        new_solutions = []
        for _ in range(self.num_ants):
            sol = np.empty(dim)
            for d in range(dim):
                l = int(np.random.choice(k, p=weights))
                mu = archive_arr[l, d]
                diffs = np.abs(archive_arr[l, d] - archive_arr[:, d])
                sigma = xi * diffs.sum() / max(k - 1, 1)
                sigma = max(sigma, 1e-6)
                sol[d] = np.random.normal(mu, sigma)

            # Clip continuous dims; round categorical last dim
            if self._prob_type == 'categorical':
                bounds = self.problem._cont_bounds
                for d, (lb, ub) in enumerate(bounds):
                    sol[d] = np.clip(sol[d], lb, ub)
                sol[-1] = float(np.clip(round(sol[-1]), 0, self.problem.num_options - 1))
            else:
                bounds = self.problem.bounds
                for d, (lb, ub) in enumerate(bounds):
                    sol[d] = np.clip(sol[d], lb, ub)
            new_solutions.append(sol)

        new_fits = [
            calculate_fitness(self.problem.evaluate(s), self.maximize)
            for s in new_solutions
        ]

        # Merge and keep best k
        all_sols = self._archive + new_solutions
        all_fits = self._archive_fit + new_fits
        order = np.argsort(all_fits)[::-1][:k]
        self._archive     = [all_sols[i] for i in order]
        self._archive_fit = [all_fits[i] for i in order]

        best_fit = self._archive_fit[0]
        best_sol = np.array(self._archive[0])
        if best_fit > self._best_fitness:
            self._best_fitness  = best_fit
            self._best_solution = best_sol.copy()

        return {
            'best_fitness':  self._best_fitness,
            'avg_fitness':   float(np.mean(self._archive_fit)),
            'best_solution': self._best_solution.copy(),
            'iteration':     self.current_iter,
        }

    # ── ACO clásico — Knapsack ────────────────────────────────────────────────

    def _init_aco_knapsack(self):
        tau0 = self.params['tau0']
        n = self.problem.n
        self._tau = np.full(n, tau0)
        self._eta = (self.problem._values /
                     np.maximum(self.problem._weights, 1e-10))

    def _step_aco_knapsack(self) -> dict:
        alpha = self.params['alpha']
        beta  = self.params['beta']
        rho   = self.params['rho']
        Q     = self.params['Q']
        n     = self.problem.n

        best_sol = None
        best_fit = -np.inf

        for _ in range(self.num_ants):
            solution = np.zeros(n)
            capacity_left = self.problem.W
            pheromone_power = self._tau ** alpha
            eta_power       = self._eta ** beta

            for i in range(n):
                if self.problem._weights[i] <= capacity_left:
                    attract = pheromone_power[i] * eta_power[i]
                    # Bernoulli: include vs exclude with neutral baseline
                    p_include = attract / (attract + 1.0)
                    if np.random.random() < p_include:
                        solution[i] = 1.0
                        capacity_left -= self.problem._weights[i]

            fit = calculate_fitness(self.problem.evaluate(solution), self.maximize)
            if fit > best_fit:
                best_fit = fit
                best_sol = solution.copy()

        # Evaporation
        self._tau = (1 - rho) * self._tau
        self._tau = np.maximum(self._tau, 1e-10)

        # Deposit from best ant — strength proportional to fitness, bounded
        if best_sol is not None and best_fit > 0:
            selected = best_sol > 0.5
            self._tau[selected] += Q * best_fit / (1.0 + best_fit)

        if best_fit > self._best_fitness:
            self._best_fitness  = best_fit
            self._best_solution = best_sol.copy()

        all_fx = [self.problem.evaluate(np.random.randint(0,2,n).astype(float))
                  for _ in range(5)]  # approx avg
        return {
            'best_fitness':  self._best_fitness,
            'avg_fitness':   float(np.mean([calculate_fitness(f, self.maximize) for f in all_fx])),
            'best_solution': self._best_solution.copy(),
            'iteration':     self.current_iter,
        }

    # ── ACO clásico — TSP ─────────────────────────────────────────────────────

    def _init_aco_tsp(self):
        n    = self.problem.n
        tau0 = self.params['tau0']
        self._tau = np.full((n, n), tau0)
        # Heuristic η[i,j] = 1 / distance[i,j]
        coords = self.problem.coords
        self._eta = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                if i != j:
                    d = float(np.linalg.norm(coords[i] - coords[j]))
                    self._eta[i, j] = 1.0 / max(d, 1e-10)

    def _step_aco_tsp(self) -> dict:
        alpha = self.params['alpha']
        beta  = self.params['beta']
        rho   = self.params['rho']
        Q     = self.params['Q']
        n     = self.problem.n

        tours = []
        fxs   = []

        for _ in range(self.num_ants):
            start = np.random.randint(n)
            visited = [start]
            unvisited = set(range(n)) - {start}

            while unvisited:
                i = visited[-1]
                probs = np.array([
                    (self._tau[i, j] ** alpha) * (self._eta[i, j] ** beta)
                    for j in unvisited
                ])
                probs_sum = probs.sum()
                if probs_sum == 0:
                    probs = np.ones(len(probs))
                    probs_sum = probs.sum()
                probs /= probs_sum
                j = np.random.choice(list(unvisited), p=probs)
                visited.append(j)
                unvisited.remove(j)

            tour = np.array(visited, dtype=float)
            fx   = self.problem.evaluate(tour)
            tours.append(tour)
            fxs.append(fx)

        # Evaporation
        self._tau *= (1 - rho)
        self._tau = np.maximum(self._tau, 1e-10)

        # Deposit from all ants (minimization: smaller fx = more pheromone)
        for tour, fx in zip(tours, fxs):
            deposit = Q / max(fx, 1e-10)
            t = tour.astype(int)
            for k in range(n):
                self._tau[t[k], t[(k + 1) % n]] += deposit
                self._tau[t[(k + 1) % n], t[k]] += deposit

        # Best in this step
        fits = [calculate_fitness(fx, self.maximize) for fx in fxs]
        best_idx = int(np.argmax(fits))
        if fits[best_idx] > self._best_fitness:
            self._best_fitness  = fits[best_idx]
            self._best_solution = tours[best_idx].copy()

        return {
            'best_fitness':  self._best_fitness,
            'avg_fitness':   float(np.mean(fits)),
            'best_solution': self._best_solution.copy(),
            'iteration':     self.current_iter,
        }

    # ── Public interface ──────────────────────────────────────────────────────

    def step(self) -> dict:
        self.current_iter += 1
        if self._prob_type in ('continuous', 'categorical'):
            result = self._step_acor()
        elif self._prob_type == 'knapsack':
            result = self._step_aco_knapsack()
        else:
            result = self._step_aco_tsp()
        result['iteration'] = self.current_iter
        return result

    def get_param_schema(self, problem_type: str) -> list[dict]:
        if problem_type in ('continuous', 'categorical'):
            return [
                {'name': 'num_ants',   'type': 'int',   'min': 2,    'max': 200, 'default': 10,
                 'description': 'Numero de hormigas'},
                {'name': 'iterations', 'type': 'int',   'min': 10,   'max': 10000,'default': 100,
                 'description': 'Numero de iteraciones'},
                {'name': 'k',          'type': 'int',   'min': 2,    'max': 100, 'default': 10,
                 'description': 'Tamano del archivo ACO-R'},
                {'name': 'q',          'type': 'float', 'min': 0.001,'max': 1.0, 'default': 0.01,
                 'description': 'Parametro q (diversificacion)'},
                {'name': 'xi',         'type': 'float', 'min': 0.001,'max': 2.0, 'default': 0.85,
                 'description': 'Escala de desviaciones xi'},
            ]
        beta_default = 5.0 if problem_type == 'tsp' else 2.0
        return [
            {'name': 'num_ants',   'type': 'int',   'min': 2,    'max': 200, 'default': 20,
             'description': 'Numero de hormigas'},
            {'name': 'iterations', 'type': 'int',   'min': 10,   'max': 10000,'default': 100,
             'description': 'Numero de iteraciones'},
            {'name': 'alpha',      'type': 'float', 'min': 0.0,  'max': 5.0, 'default': 1.0,
             'description': 'Peso de la feromona (alpha)'},
            {'name': 'beta',       'type': 'float', 'min': 0.0,  'max': 10.0,'default': beta_default,
             'description': 'Peso de la heuristica (beta)'},
            {'name': 'rho',        'type': 'float', 'min': 0.001,'max': 0.999,'default': 0.1,
             'description': 'Tasa de evaporacion rho'},
            {'name': 'Q',          'type': 'float', 'min': 0.001,'max': 1000.0,'default': 100.0,
             'description': 'Constante de deposito Q'},
            {'name': 'tau0',       'type': 'float', 'min': 0.001,'max': 10.0, 'default': 0.1,
             'description': 'Feromona inicial tau0'},
        ]
