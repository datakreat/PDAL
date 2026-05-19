RF_LIMITS = {
    "Pt": {
        "max": 100,
        "unit": "W"
    },
    "frequency": {
        "max": 100e9,
        "unit": "Hz"
    }
}


def validate_parameter(name, value):

    if name not in RF_LIMITS:
        return None

    limit = RF_LIMITS[name]

    if value > limit["max"]:
        return {
            "parameter": name,
            "reason": f"{name} exceeds max limit"
        }

    return None