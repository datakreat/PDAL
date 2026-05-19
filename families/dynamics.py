from sympy import symbols, Eq
from families.constants import g

# Define Dynamics symbols
F, m, a, p, v, W, d, KE, PE, h, P = symbols("F m a p v W d KE PE h P", real=True)
t = symbols("t", positive=True)
F_spring, k_spring, x_spring, tau_torque, r_arm, F_c, r_radius = symbols(
    "F_spring k_spring x_spring tau_torque r_arm F_c r_radius", positive=True
)

DYNAMICS_FAMILY = {
    "name": "dynamics",
    "parameters": {
        "F": {"description": "Force", "unit": "N", "dimension": "[mass] * [length] / [time]**2"},
        "m": {"description": "Mass", "unit": "kg", "dimension": "[mass]"},
        "a": {"description": "Acceleration", "unit": "m/s^2", "dimension": "[length] / [time]**2"},
        "p": {"description": "Momentum", "unit": "kg*m/s", "dimension": "[mass] * [length] / [time]"},
        "v": {"description": "Velocity", "unit": "m/s", "dimension": "[length] / [time]"},
        "W": {"description": "Work", "unit": "J", "dimension": "[mass] * [length]**2 / [time]**2"},
        "d": {"description": "Displacement", "unit": "m", "dimension": "[length]"},
        "KE": {"description": "Kinetic Energy", "unit": "J", "dimension": "[mass] * [length]**2 / [time]**2"},
        "PE": {"description": "Potential Energy", "unit": "J", "dimension": "[mass] * [length]**2 / [time]**2"},
        "h": {"description": "Height", "unit": "m", "dimension": "[length]"},
        "P": {"description": "Power", "unit": "W", "dimension": "[mass] * [length]**2 / [time]**3"},
        "t": {"description": "Time", "unit": "s", "dimension": "[time]"},
        "F_spring": {"description": "Spring force", "unit": "N", "dimension": "[mass] * [length] / [time]**2"},
        "k_spring": {"description": "Spring constant", "unit": "N/m", "dimension": "[mass] / [time]**2"},
        "x_spring": {"description": "Spring extension", "unit": "m", "dimension": "[length]"},
        "tau_torque": {"description": "Torque", "unit": "N*m", "dimension": "[mass] * [length]**2 / [time]**2"},
        "r_arm": {"description": "Lever arm radius", "unit": "m", "dimension": "[length]"},
        "F_c": {"description": "Centripetal force", "unit": "N", "dimension": "[mass] * [length] / [time]**2"},
        "r_radius": {"description": "Rotation radius", "unit": "m", "dimension": "[length]"},
    },
    "equations": [
        {
            "name": "newtons_second_law",
            "equation": Eq(F, m * a),
            "symbol_map": {"F": F, "m": m, "a": a},
        },
        {
            "name": "momentum",
            "equation": Eq(p, m * v),
            "symbol_map": {"p": p, "m": m, "v": v},
        },
        {
            "name": "work",
            "equation": Eq(W, F * d),
            "symbol_map": {"W": W, "F": F, "d": d},
        },
        {
            "name": "kinetic_energy",
            "equation": Eq(KE, 0.5 * m * v ** 2),
            "symbol_map": {"KE": KE, "m": m, "v": v},
        },
        {
            "name": "potential_energy",
            "equation": Eq(PE, m * g * h),
            "symbol_map": {"PE": PE, "m": m, "g": g, "h": h},
        },
        {
            "name": "power",
            "equation": Eq(P, W / t),
            "symbol_map": {"P": P, "W": W, "t": t},
        },
        {
            "name": "hookes_law",
            "equation": Eq(F_spring, k_spring * x_spring),
            "symbol_map": {"F_spring": F_spring, "k_spring": k_spring, "x_spring": x_spring},
        },
        {
            "name": "torque",
            "equation": Eq(tau_torque, F * r_arm),
            "symbol_map": {"tau_torque": tau_torque, "F": F, "r_arm": r_arm},
        },
        {
            "name": "centripetal_force",
            "equation": Eq(F_c, m * v**2 / r_radius),
            "symbol_map": {"F_c": F_c, "m": m, "v": v, "r_radius": r_radius},
        },
    ],
    "limits": {
        "v": {
            "hard_max": 299792458.0,
            "unit": "m/s",
            "reason": "Velocity cannot exceed the speed of light in vacuum",
        },
        "m": {
            "soft_max": 1.0e6,
            "unit": "kg",
            "reason": "Mass exceeds typical heavy transport operational limits",
        },
    },
    "defaults": {
        "m": 1.0,
        "h": 0.0,
    },
}
