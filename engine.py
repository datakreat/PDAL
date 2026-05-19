import os
from dotenv import load_dotenv

from extractor.llm_extractor import extract_parameters
from state import PhysicsState
from families.registry import FAMILIES, get_family_registry
from planner.graph_solver import ground_and_solve_physics
from validation.dimensional_checks import validate_dimension, ureg
from utils.rf_math import linear_to_db

load_dotenv()

MIN_SNR_DB = 10.0


def main():
    print("=================== 📡 Grounded Multi-Physics Engine ===================")

    # =====================================================
    # Initialize State & Get User Query
    # =====================================================
    state = PhysicsState()
    text = input("Enter Query: ")

    # =====================================================
    # LLM Domain Routing & Extraction
    # =====================================================
    extracted = extract_parameters(text)

    family_name = extracted.get("family")
    target = extracted.get("target")
    extracted_params = extracted.get("parameters", {})

    if not family_name or family_name not in FAMILIES:
        print(f"\n❌ Unsupported or unrecognized physics family: '{family_name}'")
        return

    family = FAMILIES[family_name]
    print(f"\n[Router] Selected Physics Family: '{family_name.upper()}'")
    print(f"[Router] Target Parameter to Solve: '{target or 'None (Verification Mode)'}'")

    # =====================================================
    # Dimensional Grounding & Standard SI Conversion
    # =====================================================
    print("\n[Grounding] Verifying extracted parameters...")
    for k, v in extracted_params.items():
        val = v.get("value")
        unit = v.get("unit", "")

        if k not in family["parameters"]:
            print(f"  ⚠️ Skipping unknown parameter '{k}' for family '{family_name}'")
            continue

        # Unit sanitization
        # 1. Battery C-rate unit "C" -> "1/hour"
        if family_name == "battery" and k == "C_rate" and unit.strip().upper() == "C":
            unit = "1/hour"
        # 2. Celsius temperature symbols -> "degC"
        if k in ["T", "T_limit", "dT"] and unit.strip() in ["C", "°C", "deg C", "degC", "Celsius"]:
            unit = "degC"

        param_schema = family["parameters"][k]
        expected_dim = param_schema["dimension"]

        # Verify dimensional compatibility
        is_valid = validate_dimension(val, unit, expected_dim)
        if not is_valid:
            print(
                f"\n❌ [DIMENSIONAL VIOLATION] Parameter '{k}' failed dimensional checks!"
            )
            print(
                f"   Given: {val} {unit}, Expected Dimension: {expected_dim}"
            )
            return

        # Ground and convert to SI base unit
        try:
            if expected_dim == "dimensionless":
                # Dimensionless variables are kept as linear ratios
                si_val = float(val)
            else:
                clean_unit = unit.replace("^", "**")
                q = ureg.Quantity(val, clean_unit)
                si_val = float(q.to_base_units().magnitude)

            state.add_explicit(k, si_val)
            print(f"  ✅ Grounded: {k} = {si_val} {param_schema['unit']} (SI standard)")
        except Exception as e:
            print(f"  ❌ Grounding failed for parameter '{k}': {e}")
            return

    # =====================================================
    # Domain-Specific Context Injections
    # =====================================================
    if family_name == "rf":
        if target == "Pt":
            # If target is Pt, SNR is set to the minimum linear SNR (10 dB threshold)
            required_snr_linear = 10 ** (MIN_SNR_DB / 10)
            state.add_derived("SNR", required_snr_linear)
            print(
                f"[Context] Injected SNR Target: {MIN_SNR_DB} dB ({required_snr_linear} linear)"
            )
        elif state.has("Pt") and not target:
            target = "SNR"

    # =====================================================
    # Load Equations Registry
    # =====================================================
    registry = get_family_registry(family_name)


    # =====================================================
    # Dynamic Planning & Solving & Grounding (First Pass)
    # =====================================================
    if target:
        print(f"\n[Solver] Resolving equation graph for target '{target}'...")
    else:
        print(f"\n[Solver] Resolving equation graph for physical verification...")

    report = ground_and_solve_physics(state, registry)

    # =====================================================
    # Load Fallback Defaults (Only for remaining missing variables)
    # =====================================================
    defaults = family.get("defaults", {})
    defaults_injected = False
    for k, v in defaults.items():
        if not state.has(k):
            state.add_derived(k, v)
            print(f"[Defaults] Injected fallback: {k} = {v}")
            defaults_injected = True

    # If any defaults were injected, run the solver again to propagate them
    if defaults_injected:
        print("\n[Solver] Re-running solver to propagate fallback defaults...")
        report = ground_and_solve_physics(state, registry)

    if target and not state.has(target):
        print(f"\n❌ Could not resolve target: '{target}'")
        print("\nFinal State:")
        print("Explicit:", state.explicit)
        print("Derived:", state.derived)
        return

    # =====================================================
    # Dynamic Feasibility & Limit Validations
    # =====================================================
    print("\n=================== Execution Report ===================")
    print("Equations Used:", " -> ".join(state.equations_used) if state.equations_used else "None")

    # Output solved target value
    if target and state.has(target):
        solved_val = state.get(target)
        target_schema = family["parameters"].get(target, {})
        target_unit = target_schema.get("unit", "")
        print(f"\nSolved Target Value '{target}': {solved_val} {target_unit}")

    # Output physical consistency results
    if report["violations"]:
        print("\n❌ Physical Consistency Check: FAILED")
        for violation in report["violations"]:
            print(f"  - {violation['message']}")
    else:
        print("\n✅ Physical Consistency Check: PASSED")

    # Check limits for all parameters in state
    limits = family.get("limits", {})
    limit_violations = False
    for param_name, limit in limits.items():
        if state.has(param_name):
            val = state.get(param_name)
            hard_max = limit.get("hard_max")
            hard_min = limit.get("hard_min")
            soft_max = limit.get("soft_max")
            soft_min = limit.get("soft_min")
            param_unit = limit.get("unit", "")

            if hard_max is not None and val > hard_max:
                print(f"❌ [HARD LIMIT VIOLATION] {param_name} exceeds maximum physical limit!")
                print(f"   Value: {val} {param_unit}, Max Limit: {hard_max} {param_unit}")
                print(f"   Reason: {limit.get('reason')}")
                limit_violations = True
            if hard_min is not None and val < hard_min:
                print(f"❌ [HARD LIMIT VIOLATION] {param_name} is below minimum physical limit!")
                print(f"   Value: {val} {param_unit}, Min Limit: {hard_min} {param_unit}")
                print(f"   Reason: {limit.get('reason')}")
                limit_violations = True
            if soft_max is not None and val > soft_max:
                print(f"⚠️ [SOFT LIMIT WARNING] {param_name} exceeds practical engineering limit.")
                print(f"   Value: {val} {param_unit}, Max Limit: {soft_max} {param_unit}")
                print(f"   Reason: {limit.get('reason')}")
            if soft_min is not None and val < soft_min:
                print(f"⚠️ [SOFT LIMIT WARNING] {param_name} is below practical engineering limit.")
                print(f"   Value: {val} {param_unit}, Min Limit: {soft_min} {param_unit}")
                print(f"   Reason: {limit.get('reason')}")

    if not limit_violations and not report["violations"]:
        print("✅ Limits Check: Passed.")

    # Special output conversions (e.g. SNR to dB)
    if family_name == "rf" and state.has("SNR"):
        snr_linear = state.get("SNR")
        snr_db = linear_to_db(snr_linear)
        print(f"Actual SNR (dB): {snr_db} dB")
        if snr_db >= MIN_SNR_DB:
            print("✅ Radar Link Feasible")
        else:
            print("❌ Radar Link NOT Feasible")

    # =====================================================
    # Final State
    # =====================================================
    print("\nFinal Physics State:")
    print("Explicit:", state.explicit)
    print("Derived:", state.derived)


if __name__ == "__main__":
    main()