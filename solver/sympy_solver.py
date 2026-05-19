from sympy import solve


def solve_equation(eq, target_symbol, knowns: dict):

    substituted = eq.subs(knowns)

    result = solve(substituted, target_symbol)

    if not result:
        return None

    return float(result[0])