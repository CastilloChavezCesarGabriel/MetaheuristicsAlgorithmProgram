"""Preset/sample data shown in the parameters screen.

Decoupled from the GUI so adding a benchmark function or knapsack
case doesn't require editing UI code.
"""

CONTINUOUS_SAMPLES = [
    ('Rastrigin  (1D, multimodal)', {
        'expression': 'x1**2 - 10*cos(2*pi*x1) + 10',
        'dimensions': '1', 'lower_bound_x1': '-5.12', 'upper_bound_x1': '5.12',
    }),
    ('Schwefel  (1D, deceptiva)', {
        'expression': '-x1*sin(sqrt(Abs(x1)))',
        'dimensions': '1', 'lower_bound_x1': '-500', 'upper_bound_x1': '500',
    }),
    ('Ackley  (1D, muy multimodal)', {
        'expression': '-20*exp(-0.2*Abs(x1)) - exp(cos(2*pi*x1)) + 20 + E',
        'dimensions': '1', 'lower_bound_x1': '-5', 'upper_bound_x1': '5',
    }),
    ('Himmelblau  (2D, 4 minimos globales)', {
        'expression': '(x1**2 + x2 - 11)**2 + (x1 + x2**2 - 7)**2',
        'dimensions': '2',
        'lower_bound_x1': '-5', 'upper_bound_x1': '5',
        'lower_bound_x2': '-5', 'upper_bound_x2': '5',
    }),
    ('Rosenbrock  (2D, valle banana)', {
        'expression': '(1 - x1)**2 + 100*(x2 - x1**2)**2',
        'dimensions': '2',
        'lower_bound_x1': '-2', 'upper_bound_x1': '2',
        'lower_bound_x2': '-1', 'upper_bound_x2': '3',
    }),
    ('Rastrigin  (2D)', {
        'expression': 'x1**2 - 10*cos(2*pi*x1) + x2**2 - 10*cos(2*pi*x2) + 20',
        'dimensions': '2',
        'lower_bound_x1': '-5.12', 'upper_bound_x1': '5.12',
        'lower_bound_x2': '-5.12', 'upper_bound_x2': '5.12',
    }),
]

KNAPSACK_SAMPLES = [
    ('Simple  5 objetos', {
        'n': '5',
        'weights': '2, 3, 4, 5, 9',
        'values':  '3, 4, 5, 8, 10',
        'W': '10', 'alpha': '1',
    }),
    ('Clasico  10 objetos', {
        'n': '10',
        'weights': '10, 20, 30, 40, 50, 15, 25, 35, 45, 55',
        'values':  '60, 100, 120, 80, 90, 70, 110, 95, 75, 130',
        'W': '100', 'alpha': '2',
    }),
    ('Alta densidad  15 objetos', {
        'n': '15',
        'weights': '5, 8, 3, 12, 7, 14, 6, 10, 9, 4, 11, 15, 2, 13, 1',
        'values':  '10, 14, 6, 25, 15, 30, 12, 22, 18, 8, 20, 28, 4, 24, 3',
        'W': '35', 'alpha': '3',
    }),
]

CATEGORICAL_SAMPLES = [
    ('Cuadratica + Descuento  (1D, 3 cat.)', {
        'expression': 'x1**2 - D*x1',
        'dimensions': '1',
        'lower_bound_x1': '-5', 'upper_bound_x1': '5',
        'num_options': '3', 'option_values': '1, 3, 6',
    }),
    ('Trigonometrica escalada  (1D, 4 cat.)', {
        'expression': 'sin(x1)*D + cos(x1)',
        'dimensions': '1',
        'lower_bound_x1': '-3.14159', 'upper_bound_x1': '3.14159',
        'num_options': '4', 'option_values': '0.5, 1, 2, 4',
    }),
    ('Paraboloide desplazado  (2D, 3 cat.)', {
        'expression': '(x1 - D)**2 + x2**2',
        'dimensions': '2',
        'lower_bound_x1': '-5', 'upper_bound_x1': '5',
        'lower_bound_x2': '-5', 'upper_bound_x2': '5',
        'num_options': '3', 'option_values': '-3, 0, 3',
    }),
]

# (display label, dataset file name in assets/tsp_datasets)
TSP_DATASETS = [
    ('Muestra  10 ciudades',    'city10'),
    ('Muestra  20 ciudades',    'city20'),
    ('Muestra  30 ciudades',    'city30'),
    ('Muestra  40 ciudades',    'city40'),
    ('berlin52  (52 ciudades)', 'berlin52'),
    ('eil51  (51 ciudades)',    'eil51'),
]
