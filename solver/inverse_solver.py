from sympy import solve


def solve_for(eq, target, knowns):

    substituted = eq.subs(knowns)

    result = solve(substituted, target)

    if not result:
        return None

    return float(result[0])