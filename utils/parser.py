import sympy as sp


def parse_expression(expression: str, variable_names: list[str]) -> tuple:
    """Parsea una expresión matemática y retorna (expr_sympy, lista_de_símbolos).

    Lanza ValueError si la expresión no es válida.
    """
    symbols = [sp.Symbol(name) for name in variable_names]
    local_map = {s.name: s for s in symbols}
    try:
        expr = sp.sympify(expression, locals=local_map)
    except Exception as e:
        raise ValueError(f"Expresión no parseable: {e}") from e
    return expr, symbols


def evaluate_expression(expr, symbols: list, values: list[float]) -> float:
    """Evalúa una expresión sympy sustituyendo cada símbolo por su valor."""
    subs = {symbols[i]: values[i] for i in range(len(symbols))}
    return float(expr.subs(subs))


def validate_expression(expression: str, variable_names: list[str]) -> tuple[bool, str]:
    """Valida que la expresión sea parseable y solo use las variables declaradas.

    Retorna (True, '') si es válida, (False, mensaje) si no.
    """
    try:
        expr, symbols = parse_expression(expression, variable_names)
    except ValueError as e:
        return False, str(e)

    declared = {sp.Symbol(name) for name in variable_names}
    free = expr.free_symbols
    undeclared = free - declared
    if undeclared:
        names = ', '.join(str(s) for s in sorted(undeclared, key=str))
        return False, f"Variable no declarada: {names}"

    return True, ""
