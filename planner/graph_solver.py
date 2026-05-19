from solver.sympy_solver import solve_equation

def ground_and_solve_physics(state, registry: list, tolerance: float = 0.01) -> dict:
    """
    Evaluates physical consistency of all equations in registry.
    - If all variables in an equation are known (0 missing), evaluates the LHS/RHS
      difference. If they differ by more than the tolerance, records a violation in state.
    - If exactly 1 variable is missing, solves for it using SymPy and adds to state,
      propagating the calculation to other equations.
    - Repeats until no further parameters can be solved and all possible equations have been checked.
    """
    solved_something = True
    evaluated_equations = set()
    solved_vars = []

    while solved_something:
        solved_something = False

        for eq_meta in registry:
            eq_name = eq_meta["name"]
            if eq_name in evaluated_equations:
                continue

            symbol_map = eq_meta.get("symbol_map", {})
            if not symbol_map:
                continue

            all_vars = set(symbol_map.keys())
            missing_vars = [v for v in all_vars if not state.has(v)]

            # Case A: Fully determined equation -> verify consistency
            if len(missing_vars) == 0:
                knowns = {symbol_map[k]: state.get(k) for k in all_vars}
                try:
                    lhs_val = float(eq_meta["equation"].lhs.subs(knowns).evalf())
                    rhs_val = float(eq_meta["equation"].rhs.subs(knowns).evalf())

                    diff = abs(lhs_val - rhs_val)
                    denom = max(abs(lhs_val), abs(rhs_val))
                    rel_diff = diff / denom if denom > 1e-15 else diff

                    if rel_diff > tolerance:
                        violation_msg = f"Equation '{eq_name}' violated: LHS={lhs_val:.6g}, RHS={rhs_val:.6g} (rel. diff={rel_diff:.2%})"
                        state.violations.append({
                            "type": "inconsistency",
                            "equation": eq_name,
                            "lhs": lhs_val,
                            "rhs": rhs_val,
                            "rel_diff": rel_diff,
                            "message": violation_msg
                        })
                        print(f"[Grounding] ❌ {violation_msg}")
                    else:
                        print(f"[Grounding] ✅ Equation '{eq_name}' verified (LHS={lhs_val:.6g} ≈ RHS={rhs_val:.6g})")

                    evaluated_equations.add(eq_name)
                    if eq_name not in state.equations_used:
                        state.equations_used.append(eq_name)
                except Exception as e:
                    print(f"[Grounding] ⚠️ Evaluation error on equation '{eq_name}': {e}")
                    evaluated_equations.add(eq_name)

            # Case B: Exactly 1 missing variable -> solve and propagate
            elif len(missing_vars) == 1:
                unknown = missing_vars[0]
                knowns = {symbol_map[k]: state.get(k) for k in all_vars if k != unknown}

                result = solve_equation(
                    eq_meta["equation"],
                    symbol_map[unknown],
                    knowns
                )

                if result is not None:
                    state.add_derived(unknown, result)
                    if eq_name not in state.equations_used:
                        state.equations_used.append(eq_name)
                    solved_vars.append(unknown)
                    evaluated_equations.add(eq_name)
                    print(f"[Planner] Dynamically solved '{unknown}' using '{eq_name}' = {result}")
                    solved_something = True
                    break  # Restart loop to propagate the new value

    return {
        "consistent": len(state.violations) == 0,
        "solved": solved_vars,
        "violations": state.violations
    }

def solve_dynamic_target(target: str, state, registry: list) -> bool:
    """
    Deprecated: Backward compatible entrypoint that performs grounding and
    returns True if the target parameter is successfully present in the state.
    """
    ground_and_solve_physics(state, registry)
    return state.has(target) if target else True
