import os
import re
import json
from dotenv import load_dotenv

from extractor.llm_extractor import extract_parameters
from state import PhysicsState
from families.registry import FAMILIES, get_family_registry
from planner.graph_solver import ground_and_solve_physics
from validation.dimensional_checks import validate_dimension, ureg
from utils.rf_math import linear_to_db

load_dotenv()

MIN_SNR_DB = 10.0


def extract_validation_text(text: str) -> str:
    # Try parsing as JSON first
    try:
        data = json.loads(text)
    except Exception:
        data = None

    if data is not None:
        # If it's a dict, search for common text keys
        if isinstance(data, dict):
            # Prioritized key search
            for key in ["title", "query", "description", "idea", "text", "content", "response", "message"]:
                val = data.get(key)
                if val and isinstance(val, str):
                    return val.strip()
            
            # Recursive check for nested dicts
            for k, val in data.items():
                if isinstance(val, (dict, list)):
                    extracted = extract_validation_text(json.dumps(val))
                    if extracted:
                        return extracted
            
            # Fallback: join all string values in the dict
            strings = []
            def collect_strings(d):
                if isinstance(d, dict):
                    for v in d.values():
                        collect_strings(v)
                elif isinstance(d, list):
                    for v in d:
                        collect_strings(v)
                elif isinstance(d, str):
                    strings.append(d)
            collect_strings(data)
            if strings:
                return " ".join(strings).strip()
        elif isinstance(data, list):
            # Join all elements or string values
            strings = []
            for item in data:
                if isinstance(item, str):
                    strings.append(item)
                elif isinstance(item, (dict, list)):
                    strings.append(extract_validation_text(json.dumps(item)))
            return " ".join(filter(None, strings)).strip()
        elif isinstance(data, str):
            return data.strip()

    # Fallback to string regex patterns if not JSON
    clean_text = text.strip()
    
    # Check for prefix headers like TITLE:, Idea:, Query:, Response: followed by quotes or raw text
    for prefix in ["TITLE", "IDEA", "QUERY", "RESPONSE", "CONTENT", "TEXT"]:
        # Match with quotes
        match_quotes = re.search(rf'^{prefix}:\s*["\'](.*?)["\']\s*$', clean_text, re.DOTALL | re.IGNORECASE)
        if match_quotes:
            return match_quotes.group(1).strip()
        # Match without quotes (greedy or up to newline)
        match_raw = re.search(rf'^{prefix}:\s*(.*)$', clean_text, re.DOTALL | re.IGNORECASE)
        if match_raw:
            return match_raw.group(1).strip()

    return clean_text


def replace_value_in_string(s: str, orig_val, feas_val, orig_unit: str) -> str:
    if not isinstance(s, str):
        return s
    
    # Determine possible string representations of orig_val
    if isinstance(orig_val, (int, float)):
        if float(orig_val).is_integer():
            possible_vals = [str(int(orig_val)), f"{float(orig_val):.1f}"]
        else:
            possible_vals = [str(orig_val)]
    else:
        possible_vals = [str(orig_val)]

    # Build regex pattern
    val_pattern = "(?:" + "|".join(re.escape(v) for v in possible_vals) + ")"
    
    # Format feasibility value cleanly
    if isinstance(feas_val, float) and feas_val.is_integer():
        feas_str = str(int(feas_val))
    elif isinstance(feas_val, (int, float)):
        feas_str = f"{feas_val:.4g}"
    else:
        feas_str = str(feas_val)

    if orig_unit:
        # Match value, optional space, and unit
        pattern = rf"\b{val_pattern}(\s*{re.escape(orig_unit)})\b"
        s = re.sub(pattern, rf"{feas_str}\1", s, flags=re.IGNORECASE)
        # Fallback without boundary on right in case of symbols
        pattern_no_wb = rf"\b{val_pattern}(\s*{re.escape(orig_unit)})"
        s = re.sub(pattern_no_wb, rf"{feas_str}\1", s, flags=re.IGNORECASE)
    else:
        pattern = rf"\b{val_pattern}\b"
        s = re.sub(pattern, feas_str, s)
    return s


def replace_in_json(data, corrections):
    if isinstance(data, dict):
        new_dict = {}
        for k, v in data.items():
            if k in corrections and isinstance(v, dict) and "value" in v:
                new_v = v.copy()
                new_v["value"] = corrections[k]["feasible_value"]
                new_dict[k] = new_v
            else:
                new_dict[k] = replace_in_json(v, corrections)
        return new_dict
    elif isinstance(data, list):
        return [replace_in_json(item, corrections) for item in data]
    elif isinstance(data, str):
        res_str = data
        for k, corr in corrections.items():
            res_str = replace_value_in_string(res_str, corr["original_value"], corr["feasible_value"], corr["original_unit"])
        return res_str
    else:
        return data


def validate_pdal(text: str) -> dict:
    clean_text = extract_validation_text(text)

    # =====================================================
    # LLM Domain Routing & Extraction
    # =====================================================
    extracted = extract_parameters(clean_text)

    if not extracted or not isinstance(extracted, dict):
        print("\n❌ Extraction parsing failed. No valid physics parameters could be extracted.")
        return {
            "status": "failed",
            "reasoning": "Extraction parsing failed. No valid physics parameters could be extracted.",
            "family": None,
            "target": None,
            "physical_consistency": False,
            "limits_passed": False,
            "solved_target_value": None,
            "final_state": {"explicit": {}, "derived": {}},
            "corrected_text": text,
            "equations_used": []
        }

    family_name = extracted.get("family")
    target = extracted.get("target")
    extracted_params = extracted.get("parameters", {})

    # Normalize extracted_params values to be dicts {"value": ..., "unit": ...}
    normalized_params = {}
    for k, v in extracted_params.items():
        if isinstance(v, dict):
            val = v.get("value")
            unit = v.get("unit") or v.get("units") or ""
        elif isinstance(v, (int, float)):
            val = v
            unit = ""
        elif isinstance(v, str):
            match = re.match(r"^\s*([+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\s*(.*)$", v.strip())
            if match:
                try:
                    val = float(match.group(1)) if "." in match.group(1) or "e" in match.group(1).lower() else int(match.group(1))
                except Exception:
                    val = match.group(1)
                unit = match.group(2).strip()
            else:
                val = v
                unit = ""
        else:
            val = v
            unit = ""
        normalized_params[k] = {"value": val, "unit": unit}
    extracted_params = normalized_params

    if not family_name or family_name not in FAMILIES:
        print(f"\n❌ Unsupported or unrecognized physics family: '{family_name}'")
        reasoning = extracted.get("reasoning")
        if reasoning:
            print(f"Reason: {reasoning}")
        return {
            "status": "skipped",
            "reasoning": reasoning or f"Unsupported or unrecognized physics family: '{family_name}'",
            "family": family_name,
            "target": target,
            "physical_consistency": False,
            "limits_passed": False,
            "solved_target_value": None,
            "final_state": {"explicit": {}, "derived": {}},
            "corrected_text": text,
            "equations_used": []
        }

    if not extracted_params:
        print("\nℹ️ Nothing to validate: No parameter values found in the query.")
        reasoning = extracted.get("reasoning")
        if reasoning:
            print(f"Reason: {reasoning}")
        return {
            "status": "skipped",
            "reasoning": reasoning or "Nothing to validate: No parameter values found in the query.",
            "family": family_name,
            "target": target,
            "physical_consistency": False,
            "limits_passed": False,
            "solved_target_value": None,
            "final_state": {"explicit": {}, "derived": {}},
            "corrected_text": text,
            "equations_used": []
        }

    family = FAMILIES[family_name]
    print(f"\n[Router] Selected Physics Family: '{family_name.upper()}'")
    print(f"[Router] Target Parameter to Solve: '{target or 'None (Verification Mode)'}'")

    # =====================================================
    # Initialize State
    # =====================================================
    state = PhysicsState()

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
            return {
                "status": "failed",
                "reasoning": f"Dimensional violation on parameter '{k}'. Given: {val} {unit}, Expected: {expected_dim}",
                "family": family_name,
                "target": target,
                "physical_consistency": False,
                "limits_passed": False,
                "solved_target_value": None,
                "final_state": {"explicit": state.explicit, "derived": state.derived},
                "corrected_text": text,
                "equations_used": []
            }

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
            return {
                "status": "failed",
                "reasoning": f"Grounding failed for parameter '{k}': {e}",
                "family": family_name,
                "target": target,
                "physical_consistency": False,
                "limits_passed": False,
                "solved_target_value": None,
                "final_state": {"explicit": state.explicit, "derived": state.derived},
                "corrected_text": text,
                "equations_used": []
            }

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
        return {
            "status": "failed",
            "reasoning": f"Could not resolve target parameter: '{target}'",
            "family": family_name,
            "target": target,
            "physical_consistency": False,
            "limits_passed": False,
            "solved_target_value": None,
            "final_state": {"explicit": state.explicit, "derived": state.derived},
            "corrected_text": text,
            "equations_used": state.equations_used
        }

    # =====================================================
    # Dynamic Feasibility & Limit Validations
    # =====================================================
    print("\n=================== Execution Report ===================")
    print("Equations Used:", " -> ".join(state.equations_used) if state.equations_used else "None")

    # Output solved target value
    solved_target_value = None
    if target and state.has(target):
        solved_target_value = state.get(target)
        target_schema = family["parameters"].get(target, {})
        target_unit = target_schema.get("unit", "")
        print(f"\nSolved Target Value '{target}': {solved_target_value} {target_unit}")

    # Output physical consistency results
    physical_consistency = not report["violations"]
    if report["violations"]:
        print("\n❌ Physical Consistency Check: FAILED")
        for violation in report["violations"]:
            print(f"  - {violation['message']}")
    else:
        print("\n✅ Physical Consistency Check: PASSED")

    # =====================================================
    # Collect Corrections for Feasible Values
    # =====================================================
    corrections = {}

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

            boundary_val = None
            if hard_max is not None and val > hard_max:
                print(f"❌ [HARD LIMIT VIOLATION] {param_name} exceeds maximum physical limit!")
                print(f"   Value: {val} {param_unit}, Max Limit: {hard_max} {param_unit}")
                print(f"   Reason: {limit.get('reason')}")
                limit_violations = True
                boundary_val = hard_max
            elif hard_min is not None and val < hard_min:
                print(f"❌ [HARD LIMIT VIOLATION] {param_name} is below minimum physical limit!")
                print(f"   Value: {val} {param_unit}, Min Limit: {hard_min} {param_unit}")
                print(f"   Reason: {limit.get('reason')}")
                limit_violations = True
                boundary_val = hard_min
            elif soft_max is not None and val > soft_max:
                print(f"⚠️ [SOFT LIMIT WARNING] {param_name} exceeds practical engineering limit.")
                print(f"   Value: {val} {param_unit}, Max Limit: {soft_max} {param_unit}")
                print(f"   Reason: {limit.get('reason')}")
                boundary_val = soft_max
            elif soft_min is not None and val < soft_min:
                print(f"⚠️ [SOFT LIMIT WARNING] {param_name} is below practical engineering limit.")
                print(f"   Value: {val} {param_unit}, Min Limit: {soft_min} {param_unit}")
                print(f"   Reason: {limit.get('reason')}")
                boundary_val = soft_min

            if boundary_val is not None and param_name in extracted_params:
                original_val = extracted_params[param_name]["value"]
                extracted_unit = extracted_params[param_name].get("unit", "")
                
                # Convert limit boundary back to extracted unit
                limit_unit = limit.get("unit", "")
                if limit_unit and extracted_unit and limit_unit != extracted_unit:
                    try:
                        q_limit = ureg.Quantity(boundary_val, limit_unit)
                        feasible_val = float(q_limit.to(extracted_unit).magnitude)
                    except Exception:
                        feasible_val = boundary_val
                else:
                    feasible_val = boundary_val
                
                corrections[param_name] = {
                    "original_value": original_val,
                    "original_unit": extracted_unit,
                    "feasible_value": feasible_val
                }

    limits_passed = not limit_violations
    if limits_passed and physical_consistency:
        print("✅ Limits Check: Passed.")

    # Calculate corrections from physical consistency violations
    if report["violations"]:
        from solver.sympy_solver import solve_equation
        for violation in report["violations"]:
            eq_name = violation.get("equation")
            eq_meta = next((eq for eq in registry if eq["name"] == eq_name), None)
            if eq_meta:
                symbol_map = eq_meta.get("symbol_map", {})
                for k in symbol_map.keys():
                    if k in state.explicit and k in extracted_params:
                        # Solve for parameter k using remaining variables in the equation
                        unknown_symbol = symbol_map[k]
                        knowns = {symbol_map[other_k]: state.get(other_k) for other_k in symbol_map.keys() if other_k != k and state.has(other_k)}
                        try:
                            solved_val_si = float(solve_equation(eq_meta["equation"], unknown_symbol, knowns))
                            param_schema = family["parameters"][k]
                            extracted_unit = extracted_params[k].get("unit", "")
                            
                            if param_schema["dimension"] == "dimensionless":
                                feasible_val = solved_val_si
                            else:
                                clean_unit = extracted_unit.replace("^", "**")
                                q_si = ureg.Quantity(solved_val_si, ureg.Quantity(1, clean_unit).to_base_units().units)
                                feasible_val = float(q_si.to(clean_unit).magnitude)
                            
                            corrections[k] = {
                                "original_value": extracted_params[k]["value"],
                                "original_unit": extracted_unit,
                                "feasible_value": feasible_val
                            }
                        except Exception as e:
                            print(f"[Corrections] Failed to compute consistent value for {k}: {e}")

    # Special output conversions (e.g. SNR to dB)
    rf_details = {}
    if family_name == "rf" and state.has("SNR"):
        snr_linear = state.get("SNR")
        snr_db = linear_to_db(snr_linear)
        rf_details["actual_snr_db"] = snr_db
        rf_details["radar_link_feasible"] = (snr_db >= MIN_SNR_DB)
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

    # =====================================================
    # Apply Corrections & Validation Formula in Place
    # =====================================================
    is_json = False
    try:
        json_data = json.loads(text)
        is_json = True
    except Exception:
        json_data = None

    formulas_str = ", ".join(state.equations_used) if state.equations_used else "None"

    if is_json and json_data is not None:
        corrected_json_data = replace_in_json(json_data, corrections)
        if isinstance(corrected_json_data, dict):
            corrected_json_data["validation_formula"] = formulas_str
        corrected_text = json.dumps(corrected_json_data, indent=2)
    else:
        corrected_text = text
        for k, corr in corrections.items():
            corrected_text = replace_value_in_string(
                corrected_text,
                corr["original_value"],
                corr["feasible_value"],
                corr["original_unit"]
            )
        # For raw string, append validation formula metadata
        corrected_text += f"\n[Validation Formula: {formulas_str}]"

    return {
        "status": "success",
        "reasoning": extracted.get("reasoning", ""),
        "family": family_name,
        "target": target,
        "physical_consistency": physical_consistency,
        "limits_passed": limits_passed,
        "solved_target_value": solved_target_value,
        "final_state": {
            "explicit": state.explicit,
            "derived": state.derived
        },
        "violations": report["violations"],
        "rf_details": rf_details,
        "corrected_text": corrected_text,
        "equations_used": state.equations_used
    }


if __name__ == "__main__":
    import sys
    query = sys.argv[1] if len(sys.argv) > 1 else input("Enter Query: ")
    res = validate_pdal(query)
    import pprint
    print("\n=================== Validation Results Dict ===================")
    pprint.pprint(res)