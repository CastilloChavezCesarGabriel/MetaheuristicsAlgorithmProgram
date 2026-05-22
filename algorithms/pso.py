import numpy as np

from algorithms.base_algorithm import BaseAlgorithm
from problems.base_problem import calculate_fitness


def _sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))


def _eval_pso(problem, pos, maximize, prob_type):
    if prob_type == 'knapsack':
        binary = (_sigmoid(pos) > 0.5).astype(float)
        fx = problem.evaluate(binary)
    elif prob_type == 'tsp':
        route = np.argsort(pos).astype(float)
        fx = problem.evaluate(route)
    else:
        fx = problem.evaluate(pos)
    return calculate_fitness(fx, maximize)


class PSO(BaseAlgorithm):

    def initialize(self, problem, params: dict, maximize: bool):
        from problems import prob_type_of

        self.problem = problem
        self.params = params
        self.maximize = maximize
        self.current_iter = 0
        self.max_iters = params['iterations']

        self._prob_type = prob_type_of(problem)

        n = params['num_particles']
        self.w    = params['w']
        self.c1   = params['c1']
        self.c2   = params['c2']
        self.vmax = params.get('vmax', 5.0)

        # Effective bounds for position clipping
        if self._prob_type == 'tsp':
            dim = problem.n
            self._bounds_eff = np.array([(0.0, 1.0)] * dim)
        elif self._prob_type == 'knapsack':
            dim = problem.n
            self._bounds_eff = np.array([(-6.0, 6.0)] * dim)  # sigmoid space
        else:
            self._bounds_eff = np.array(problem.bounds)
            dim = len(self._bounds_eff)

        lb = self._bounds_eff[:, 0]
        ub = self._bounds_eff[:, 1]

        if self._prob_type == 'tsp':
            self.positions = np.random.uniform(0, 1, (n, dim))
        else:
            self.positions = np.array([problem.generate_random_solution() for _ in range(n)])
            # clip to bounds
            self.positions = np.clip(self.positions, lb, ub)

        self.velocities = np.zeros((n, dim))
        self.pbest_pos  = self.positions.copy()
        self.pbest_fit  = np.array([
            _eval_pso(problem, p, maximize, self._prob_type)
            for p in self.positions
        ])

        gbest_idx = int(np.argmax(self.pbest_fit))
        self.gbest_pos = self.pbest_pos[gbest_idx].copy()
        self.gbest_fit = float(self.pbest_fit[gbest_idx])

    def step(self) -> dict:
        n = len(self.positions)
        lb = self._bounds_eff[:, 0]
        ub = self._bounds_eff[:, 1]

        r1 = np.random.random(self.positions.shape)
        r2 = np.random.random(self.positions.shape)

        self.velocities = (self.w * self.velocities
                           + self.c1 * r1 * (self.pbest_pos - self.positions)
                           + self.c2 * r2 * (self.gbest_pos - self.positions))
        self.velocities = np.clip(self.velocities, -self.vmax, self.vmax)
        self.positions  = np.clip(self.positions + self.velocities, lb, ub)

        fitnesses = np.array([
            _eval_pso(self.problem, p, self.maximize, self._prob_type)
            for p in self.positions
        ])

        improved = fitnesses > self.pbest_fit
        self.pbest_pos[improved] = self.positions[improved]
        self.pbest_fit[improved] = fitnesses[improved]

        gbest_idx = int(np.argmax(self.pbest_fit))
        if self.pbest_fit[gbest_idx] > self.gbest_fit:
            self.gbest_pos = self.pbest_pos[gbest_idx].copy()
            self.gbest_fit = float(self.pbest_fit[gbest_idx])

        self.current_iter += 1

        best_pos = self.gbest_pos
        if self._prob_type == 'tsp':
            best_pos = np.argsort(self.gbest_pos).astype(float)
        elif self._prob_type == 'knapsack':
            best_pos = (_sigmoid(self.gbest_pos) > 0.5).astype(float)

        return {
            'best_fitness':  self.gbest_fit,
            'avg_fitness':   float(np.mean(fitnesses)),
            'best_solution': best_pos.copy(),
            'iteration':     self.current_iter,
        }

    def get_param_schema(self, problem_type: str) -> list[dict]:
        return [
            {'name': 'num_particles', 'type': 'int',   'min': 2,   'max': 500,  'default': 30,
             'description': 'Numero de particulas'},
            {'name': 'iterations',    'type': 'int',   'min': 10,  'max': 10000,'default': 100,
             'description': 'Numero de iteraciones'},
            {'name': 'w',             'type': 'float', 'min': 0.0, 'max': 2.0,  'default': 0.7,
             'description': 'Inercia w'},
            {'name': 'c1',            'type': 'float', 'min': 0.0, 'max': 4.0,  'default': 1.5,
             'description': 'Coeficiente cognitivo c1'},
            {'name': 'c2',            'type': 'float', 'min': 0.0, 'max': 4.0,  'default': 1.5,
             'description': 'Coeficiente social c2'},
            {'name': 'vmax',          'type': 'float', 'min': 0.01,'max': 100.0,'default': 5.0,
             'description': 'Velocidad maxima'},
        ]

    @property
    def is_finished(self) -> bool:
        return self.current_iter >= self.max_iters
