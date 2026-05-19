from solver.sympy_solver import solve_equation


def execute_equation(eq_meta, target, state):

    symbol_map = eq_meta["symbol_map"]

    knowns = {}

    for inp in eq_meta["inputs"]:

        value = state.get(inp)

        if value is None:

            print(f"Missing input: {inp}")

            return None

        knowns[symbol_map[inp]] = value

    result = solve_equation(
        eq_meta["equation"],
        symbol_map[target],
        knowns
    )

    return result