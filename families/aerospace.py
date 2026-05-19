from sympy import symbols, Eq, log
from families.constants import g, G_grav

# Define Aerospace symbols
L_lift, D_drag, rho_air, v_air, A_wing, C_L, C_D, T_thrust, m, TWR = symbols(
    "L_lift D_drag rho_air v_air A_wing C_L C_D T_thrust m TWR", positive=True
)
dv, I_sp, m0, mf, v_orbit, M_body, r, T_orbit, M_mach, a_sound = symbols(
    "dv I_sp m0 mf v_orbit M_body r T_orbit M_mach a_sound", positive=True
)

# Note: SymPy pi is used for orbital period calculation
from sympy import pi

AEROSPACE_FAMILY = {
    "name": "aerospace",
    "parameters": {
        "L_lift": {"description": "Lift force", "unit": "N", "dimension": "[mass] * [length] / [time]**2"},
        "D_drag": {"description": "Drag force", "unit": "N", "dimension": "[mass] * [length] / [time]**2"},
        "rho_air": {"description": "Air density", "unit": "kg/m^3", "dimension": "[mass] / [length]**3"},
        "v_air": {"description": "Airspeed / velocity", "unit": "m/s", "dimension": "[length] / [time]"},
        "A_wing": {"description": "Wing reference area", "unit": "m^2", "dimension": "[length]**2"},
        "C_L": {"description": "Lift coefficient", "unit": "linear", "dimension": "dimensionless"},
        "C_D": {"description": "Drag coefficient", "unit": "linear", "dimension": "dimensionless"},
        "T_thrust": {"description": "Thrust force", "unit": "N", "dimension": "[mass] * [length] / [time]**2"},
        "m": {"description": "Aircraft or rocket mass", "unit": "kg", "dimension": "[mass]"},
        "TWR": {"description": "Thrust-to-weight ratio", "unit": "linear", "dimension": "dimensionless"},
        "dv": {"description": "Delta-v velocity change", "unit": "m/s", "dimension": "[length] / [time]"},
        "I_sp": {"description": "Specific impulse", "unit": "s", "dimension": "[time]"},
        "m0": {"description": "Initial launch mass", "unit": "kg", "dimension": "[mass]"},
        "mf": {"description": "Final empty mass", "unit": "kg", "dimension": "[mass]"},
        "v_orbit": {"description": "Orbital velocity", "unit": "m/s", "dimension": "[length] / [time]"},
        "M_body": {"description": "Mass of central body", "unit": "kg", "dimension": "[mass]"},
        "r": {"description": "Orbital radius", "unit": "m", "dimension": "[length]"},
        "T_orbit": {"description": "Orbital period", "unit": "s", "dimension": "[time]"},
        "M_mach": {"description": "Mach number", "unit": "linear", "dimension": "dimensionless"},
        "a_sound": {"description": "Speed of sound", "unit": "m/s", "dimension": "[length] / [time]"},
    },
    "equations": [
        {
            "name": "lift_equation",
            "equation": Eq(L_lift, 0.5 * rho_air * v_air**2 * A_wing * C_L),
            "symbol_map": {"L_lift": L_lift, "rho_air": rho_air, "v_air": v_air, "A_wing": A_wing, "C_L": C_L},
        },
        {
            "name": "drag_equation",
            "equation": Eq(D_drag, 0.5 * rho_air * v_air**2 * A_wing * C_D),
            "symbol_map": {"D_drag": D_drag, "rho_air": rho_air, "v_air": v_air, "A_wing": A_wing, "C_D": C_D},
        },
        {
            "name": "thrust_to_weight",
            "equation": Eq(TWR, T_thrust / (m * g)),
            "symbol_map": {"TWR": TWR, "T_thrust": T_thrust, "m": m, "g": g},
        },
        {
            "name": "rocket_equation",
            "equation": Eq(dv, I_sp * g * log(m0 / mf)),
            "symbol_map": {"dv": dv, "I_sp": I_sp, "g": g, "m0": m0, "mf": mf},
        },
        {
            "name": "orbital_velocity",
            "equation": Eq(v_orbit**2, G_grav * M_body / r),
            "symbol_map": {"v_orbit": v_orbit, "G_grav": G_grav, "M_body": M_body, "r": r},
        },
        {
            "name": "orbital_period",
            "equation": Eq(T_orbit**2, 4 * pi**2 * r**3 / (G_grav * M_body)),
            "symbol_map": {"T_orbit": T_orbit, "r": r, "G_grav": G_grav, "M_body": M_body},
        },
        {
            "name": "mach_number",
            "equation": Eq(M_mach, v_air / a_sound),
            "symbol_map": {"M_mach": M_mach, "v_air": v_air, "a_sound": a_sound},
        },
    ],
    "limits": {
        "M_mach": {
            "soft_max": 5.0,
            "unit": "linear",
            "reason": "Velocity enters hypersonic regime, standard aerodynamics may degrade",
        },
        "TWR": {
            "soft_min": 1.0,
            "unit": "linear",
            "reason": "Thrust-to-weight ratio below 1.0 cannot lift off from the ground",
        },
    },
    "defaults": {
        "rho_air": 1.225,
        "a_sound": 340.29,
        "M_body": 5.972e24,  # Earth mass in kg
    },
}
