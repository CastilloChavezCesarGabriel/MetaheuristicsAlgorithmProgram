"""Single source of truth for problem and algorithm display data.

All GUI screens import from here. To rename, reorder, or add an entry,
edit this file only — every screen picks up the change.
"""

# Each entry: (code, full_label, short_label, description)
PROBLEMS = [
    ('continuous',  'Funcion Continua', 'f(x)',
     'Optimiza funciones matematicas\nen 1D o 2D con variables reales'),
    ('knapsack',    'Knapsack',         '[ ]',
     'Problema clasico de la mochila\ncon restriccion de peso'),
    ('categorical', 'Categorica Mixta', 'x,D',
     'Variables continuas + categoricas\ncon opciones discretas'),
    ('tsp',         'TSP',              'TSP',
     'Problema del viajante\ncon visualizacion de rutas'),
]

# Each entry: (code, full_label, short_label, description)
ALGORITHMS = [
    ('ga',  'Algoritmo Genetico',       'GA',
     'Seleccion, cruce y mutacion\ninspirados en la evolucion'),
    ('pso', 'Particle Swarm',           'PSO',
     'Enjambre de particulas que\nexploran el espacio de busqueda'),
    ('aco', 'Ant Colony',               'ACO',
     'Feromonas artificiales guian\nla busqueda colectiva'),
    ('ais', 'Artificial Immune System', 'AIS',
     'Clonacion y mutacion basadas\nen el sistema inmunologico'),
    ('de',  'Evolucion Diferencial',    'DE',
     'Perturbacion diferencial\npara optimizacion continua'),
]

PROBLEM_LABELS = {code: full for code, full, _short, _desc in PROBLEMS}
PROBLEM_SHORT  = {code: short for code, _full, short, _desc in PROBLEMS}
ALGORITHM_LABELS = {code: full for code, full, _short, _desc in ALGORITHMS}
ALGORITHM_SHORT  = {code: short for code, _full, short, _desc in ALGORITHMS}
