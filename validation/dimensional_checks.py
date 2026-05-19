from pint import UnitRegistry

ureg = UnitRegistry()


def validate_dimension(
    value: float, unit: str, expected_dimension: str
) -> bool:
    """
    Checks if a given value with a unit maps to the expected physics dimension.
    e.g. validate_dimension(77, 'GHz', '1 / [time]') -> True
    validate_dimension(200, 'K', '[temperature]') -> True
    validate_dimension(10, 'W', '[length]') -> False
    """
    if expected_dimension == "dimensionless":
        if not unit or unit.lower() in [
            "linear",
            "dimensionless",
            "1",
            "ratio",
        ]:
            return True
        try:
            q = ureg.Quantity(1, unit)
            return q.dimensionless
        except Exception:
            return False

    try:
        # Standardize unit parsing
        clean_unit = unit.replace("^", "**")
        q = ureg.Quantity(1, clean_unit)
        actual_dimension = str(q.dimensionality)

        # Standardize string representations for direct comparison
        norm_actual = actual_dimension.replace(" ", "").replace("**", "^")
        norm_expected = expected_dimension.replace(" ", "").replace("**", "^")

        return norm_actual == norm_expected

    except Exception as e:
        print(f"[Dimension Check Error] Failed to parse dimensions: {e}")
        return False

