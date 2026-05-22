# -*- coding: utf-8 -*-
import sympy as sp
from utils.parser import validate_expression, parse_expression


# ---------------------------------------------------------------------------
# Validadores globales (sección 8 — aplican a todos los problemas/algoritmos)
# ---------------------------------------------------------------------------

def validate_population_size(value) -> tuple[bool, str]:
    try:
        v = int(value)
    except (TypeError, ValueError):
        return False, "El tamano de poblacion debe ser un entero"
    if v < 4:
        return False, "El tamano de poblacion debe ser >= 4"
    return True, ""


def validate_iterations(value) -> tuple[bool, str]:
    try:
        v = int(value)
    except (TypeError, ValueError):
        return False, "El numero de iteraciones debe ser un entero"
    if v < 10:
        return False, "El numero de iteraciones debe ser >= 10"
    return True, ""


def validate_rate(value, name: str = "tasa") -> tuple[bool, str]:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return False, f"{name} debe ser un numero"
    if not (0.0 <= v <= 1.0):
        return False, f"{name} debe estar en [0, 1]"
    return True, ""


def validate_convergence_n(value, max_iterations: int) -> tuple[bool, str]:
    try:
        v = int(value)
    except (TypeError, ValueError):
        return False, "N de convergencia debe ser un entero"
    if v < 1:
        return False, "N de convergencia debe ser >= 1"
    if v > max_iterations:
        return False, f"N de convergencia debe ser <= iteraciones ({max_iterations})"
    return True, ""


# ---------------------------------------------------------------------------
# Validadores por problema (sección 8)
# ---------------------------------------------------------------------------

def _validate_bounds(bounds: list[tuple], dimensions: int) -> tuple[bool, str]:
    if len(bounds) != dimensions:
        return False, f"Se esperan {dimensions} pares de limites"
    for i, (lb, ub) in enumerate(bounds):
        try:
            lb, ub = float(lb), float(ub)
        except (TypeError, ValueError):
            return False, f"Los limites de x{i+1} deben ser numericos"
        if lb >= ub:
            return False, f"El limite inferior de x{i+1} debe ser menor al superior"
    return True, ""


def validate_continuous_params(expression: str, dimensions: int,
                                bounds: list[tuple]) -> tuple[bool, str]:
    if dimensions not in (1, 2):
        return False, "Las dimensiones deben ser 1 o 2"

    var_names = [f"x{i+1}" for i in range(dimensions)]
    ok, err = validate_expression(expression, var_names)
    if not ok:
        return False, err

    expr_obj, _ = parse_expression(expression, var_names)
    unused = {sp.Symbol(n) for n in var_names} - expr_obj.free_symbols
    if unused:
        names = ', '.join(str(s) for s in sorted(unused, key=str))
        return False, (f"Variable(s) declarada(s) pero no usada(s) en la expresion: {names}. "
                       f"Ajusta la expresion o reduce dimensions a {dimensions - len(unused)}.")

    return _validate_bounds(bounds, dimensions)


def validate_knapsack_params(n: int, weights: list, values: list,
                              W: float, alpha: float) -> tuple[bool, str]:
    try:
        n = int(n)
    except (TypeError, ValueError):
        return False, "El numero de objetos debe ser un entero"
    if n < 2:
        return False, "El numero de objetos debe ser >= 2"

    if len(weights) != n or len(values) != n:
        return False, "La cantidad de pesos y valores debe coincidir con n"

    for i, w in enumerate(weights):
        try:
            w = float(w)
        except (TypeError, ValueError):
            return False, f"El peso del objeto {i+1} debe ser numerico"
        if w <= 0:
            return False, f"El peso del objeto {i+1} debe ser > 0"

    for i, v in enumerate(values):
        try:
            v = float(v)
        except (TypeError, ValueError):
            return False, f"El valor del objeto {i+1} debe ser numerico"
        if v <= 0:
            return False, f"El valor del objeto {i+1} debe ser > 0"

    try:
        W = float(W)
    except (TypeError, ValueError):
        return False, "La capacidad W debe ser numerica"
    if W <= 0:
        return False, "La capacidad W debe ser > 0"

    try:
        alpha = float(alpha)
    except (TypeError, ValueError):
        return False, "El factor de penalizacion alpha debe ser numerico"
    if alpha <= 0:
        return False, "El factor de penalizacion alpha debe ser > 0"

    return True, ""


def validate_categorical_params(expression: str, dimensions: int,
                                  bounds: list[tuple], num_options: int,
                                  option_values: list,
                                  operator: str) -> tuple[bool, str]:
    if dimensions not in (1, 2):
        return False, "Las dimensiones deben ser 1 o 2"

    var_names = [f"x{i+1}" for i in range(dimensions)] + ['D']
    ok, err = validate_expression(expression, var_names)
    if not ok:
        return False, err

    expr_obj, _ = parse_expression(expression, var_names)
    unused = {sp.Symbol(n) for n in var_names} - expr_obj.free_symbols
    if unused:
        names = ', '.join(str(s) for s in sorted(unused, key=str))
        return False, f"Variable(s) declarada(s) pero no usada(s) en la expresion: {names}"

    ok, err = _validate_bounds(bounds, dimensions)
    if not ok:
        return False, err

    try:
        num_options = int(num_options)
    except (TypeError, ValueError):
        return False, "El numero de opciones categoricas debe ser un entero"
    if num_options < 2:
        return False, "Debe haber al menos 2 opciones categoricas"

    if len(option_values) != num_options:
        return False, "La cantidad de valores no coincide con el numero de opciones"
    for i, v in enumerate(option_values):
        try:
            float(v)
        except (TypeError, ValueError):
            return False, f"El valor de la opcion {i+1} debe ser numerico"

    if operator not in ('+', '-', '*', '/'):
        return False, "El operador debe ser uno de: +, -, *, /"

    return True, ""


def validate_tsp_params(n: int, coords: list[tuple]) -> tuple[bool, str]:
    try:
        n = int(n)
    except (TypeError, ValueError):
        return False, "El numero de ciudades debe ser un entero"
    if n < 3:
        return False, "El numero de ciudades debe ser >= 3"

    if len(coords) != n:
        return False, f"Se esperan {n} pares de coordenadas"

    parsed = []
    for i, coord in enumerate(coords):
        try:
            x, y = float(coord[0]), float(coord[1])
        except (TypeError, ValueError, IndexError):
            return False, f"Las coordenadas de la ciudad {i+1} deben ser numericas"
        parsed.append((x, y))

    seen = set()
    for i, (x, y) in enumerate(parsed):
        if (x, y) in seen:
            return False, f"La ciudad {i+1} tiene coordenadas duplicadas"
        seen.add((x, y))

    return True, ""


# ---------------------------------------------------------------------------
# Validadores por algoritmo (sección 8)
# ---------------------------------------------------------------------------

def validate_ga_params(tournament_size, population_size,
                        blx_alpha) -> tuple[bool, str]:
    try:
        t = int(tournament_size)
    except (TypeError, ValueError):
        return False, "El tamano de torneo debe ser un entero"
    if t < 2:
        return False, "El tamano de torneo debe ser >= 2"
    try:
        p = int(population_size)
    except (TypeError, ValueError):
        return False, "El tamano de poblacion debe ser un entero"
    if t >= p:
        return False, "El tamano de torneo debe ser < tamano de poblacion"

    try:
        alpha = float(blx_alpha)
    except (TypeError, ValueError):
        return False, "El alpha de BLX-alpha debe ser numerico"
    if alpha < 0:
        return False, "El alpha de BLX-alpha debe ser >= 0"

    return True, ""


def validate_pso_params(c1, c2, w, vmax) -> tuple[bool, str]:
    for val, name in ((c1, 'c1'), (c2, 'c2')):
        try:
            v = float(val)
        except (TypeError, ValueError):
            return False, f"{name} debe ser numerico"
        if v <= 0:
            return False, f"{name} debe ser > 0"

    try:
        w = float(w)
    except (TypeError, ValueError):
        return False, "w debe ser numerico"
    if not (0.0 <= w <= 2.0):
        return False, "w debe estar en [0, 2]"

    try:
        vmax = float(vmax)
    except (TypeError, ValueError):
        return False, "vmax debe ser numerico"
    if vmax <= 0:
        return False, "vmax debe ser > 0"

    return True, ""


def validate_aco_params(alpha, beta, rho, Q, tau0,
                         num_ants) -> tuple[bool, str]:
    for val, name in ((alpha, 'alpha'), (beta, 'beta')):
        try:
            v = float(val)
        except (TypeError, ValueError):
            return False, f"{name} debe ser numerico"
        if v < 0:
            return False, f"{name} debe ser >= 0"

    try:
        rho = float(rho)
    except (TypeError, ValueError):
        return False, "rho debe ser numerico"
    if not (0.0 < rho < 1.0):
        return False, "rho debe estar en (0, 1)"

    for val, name in ((Q, 'Q'), (tau0, 'tau0')):
        try:
            v = float(val)
        except (TypeError, ValueError):
            return False, f"{name} debe ser numerico"
        if v <= 0:
            return False, f"{name} debe ser > 0"

    try:
        na = int(num_ants)
    except (TypeError, ValueError):
        return False, "El numero de hormigas debe ser un entero"
    if na < 2:
        return False, "El numero de hormigas debe ser >= 2"

    return True, ""


def validate_ais_params(beta, d, rho) -> tuple[bool, str]:
    try:
        beta = float(beta)
    except (TypeError, ValueError):
        return False, "beta debe ser numerico"
    if beta <= 0:
        return False, "beta debe ser > 0"

    try:
        d = float(d)
    except (TypeError, ValueError):
        return False, "d debe ser numerico"
    if not (0.0 < d < 1.0):
        return False, "d debe estar en (0, 1)"

    try:
        rho = float(rho)
    except (TypeError, ValueError):
        return False, "rho debe ser numerico"
    if rho <= 0:
        return False, "rho debe ser > 0"

    return True, ""


def validate_de_params(F, CR, population_size) -> tuple[bool, str]:
    try:
        F = float(F)
    except (TypeError, ValueError):
        return False, "F debe ser numerico"
    if not (0.0 < F <= 2.0):
        return False, "F debe estar en (0, 2]"

    try:
        CR = float(CR)
    except (TypeError, ValueError):
        return False, "CR debe ser numerico"
    if not (0.0 <= CR <= 1.0):
        return False, "CR debe estar en [0, 1]"

    ok, err = validate_population_size(population_size)
    if not ok:
        return False, err

    return True, ""
