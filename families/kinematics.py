from sympy import symbols, Eq
from families.constants import g

# Define Kinematics symbols
s, u, v, a = symbols("s u v a", real=True)
t = symbols("t", positive=True)

KINEMATICS_FAMILY = {
    "name": "kinematics",
    "parameters": {
        "s": {"description": "Displacement", "unit": "m", "dimension": "[length]"},
        "u": {"description": "Initial velocity", "unit": "m/s", "dimension": "[length] / [time]"},
        "v": {"description": "Final velocity", "unit": "m/s", "dimension": "[length] / [time]"},
        "a": {"description": "Acceleration", "unit": "m/s^2", "dimension": "[length] / [time]**2"},
        "t": {"description": "Time elapsed", "unit": "s", "dimension": "[time]"},
    },
    "equations": [
        {
            "name": "suvat_v",
            "equation": Eq(v, u + a * t),
            "symbol_map": {"v": v, "u": u, "a": a, "t": t},
        },
        {
            "name": "suvat_s",
            "equation": Eq(s, u * t + 0.5 * a * t ** 2),
            "symbol_map": {"s": s, "u": u, "a": a, "t": t},
        },
        {
            "name": "suvat_v_squared",
            "equation": Eq(v ** 2, u ** 2 + 2 * a * s),
            "symbol_map": {"v": v, "u": u, "a": a, "s": s},
        },
        {
            "name": "suvat_avg_v",
            "equation": Eq(s, 0.5 * (u + v) * t),
            "symbol_map": {"s": s, "u": u, "v": v, "t": t},
        },
        {
            "name": "suvat_s_no_u",
            "equation": Eq(s, v * t - 0.5 * a * t**2),
            "symbol_map": {"s": s, "v": v, "a": a, "t": t},
        },
        {
            "name": "free_fall_gravity",
            "equation": Eq(a, g),
            "symbol_map": {"a": a, "g": g},
        },
    ],
    "limits": {
        "v": {
            "hard_max": 299792458.0,
            "unit": "m/s",
            "reason": "Velocity cannot exceed the speed of light in vacuum",
        },
        "a": {
            "soft_max": 1000.0,
            "unit": "m/s^2",
            "reason": "Acceleration exceeds extreme structural tolerances for physical payloads",
        },
    },
    "defaults": {
        "u": 0.0,  # default to starting from rest if initial velocity is missing
    },
}
