from sympy import symbols, Eq

# Define Circuits symbols
V, I, R, P, Q = symbols("V I R P Q", positive=True)
t = symbols("t", positive=True)
C_cap, E_field, d_dist, rho_resistivity, L_wire, A_wire = symbols(
    "C_cap E_field d_dist rho_resistivity L_wire A_wire", positive=True
)

CIRCUITS_FAMILY = {
    "name": "circuits",
    "parameters": {
        "V": {"description": "Voltage", "unit": "V", "dimension": "[mass] * [length]**2 / [time]**3 / [current]"},
        "I": {"description": "Current", "unit": "A", "dimension": "[current]"},
        "R": {"description": "Resistance", "unit": "ohm", "dimension": "[mass] * [length]**2 / [time]**3 / [current]**2"},
        "P": {"description": "Power", "unit": "W", "dimension": "[mass] * [length]**2 / [time]**3"},
        "Q": {"description": "Charge", "unit": "C", "dimension": "[current] * [time]"},
        "t": {"description": "Time", "unit": "s", "dimension": "[time]"},
        "C_cap": {"description": "Capacitance", "unit": "F", "dimension": "[current]**2 * [time]**4 / [mass] / [length]**2"},
        "E_field": {"description": "Electric Field Strength", "unit": "V/m", "dimension": "[mass] * [length] / [time]**3 / [current]"},
        "d_dist": {"description": "Distance / separation", "unit": "m", "dimension": "[length]"},
        "rho_resistivity": {"description": "Electrical resistivity", "unit": "ohm*m", "dimension": "[mass] * [length]**3 / [time]**3 / [current]**2"},
        "L_wire": {"description": "Wire length", "unit": "m", "dimension": "[length]"},
        "A_wire": {"description": "Wire cross-sectional area", "unit": "m^2", "dimension": "[length]**2"},
    },
    "equations": [
        {
            "name": "ohms_law",
            "equation": Eq(V, I * R),
            "symbol_map": {"V": V, "I": I, "R": R},
        },
        {
            "name": "electrical_power",
            "equation": Eq(P, V * I),
            "symbol_map": {"P": P, "V": V, "I": I},
        },
        {
            "name": "charge",
            "equation": Eq(Q, I * t),
            "symbol_map": {"Q": Q, "I": I, "t": t},
        },
        {
            "name": "capacitor_charge",
            "equation": Eq(Q, C_cap * V),
            "symbol_map": {"Q": Q, "C_cap": C_cap, "V": V},
        },
        {
            "name": "electric_field",
            "equation": Eq(E_field, V / d_dist),
            "symbol_map": {"E_field": E_field, "V": V, "d_dist": d_dist},
        },
        {
            "name": "wire_resistance",
            "equation": Eq(R, rho_resistivity * L_wire / A_wire),
            "symbol_map": {"R": R, "rho_resistivity": rho_resistivity, "L_wire": L_wire, "A_wire": A_wire},
        },
    ],
    "limits": {
        "R": {
            "soft_max": 1.0e9,
            "unit": "ohm",
            "reason": "Resistance exceeds practical insulating limits",
        },
        "I": {
            "soft_max": 1000.0,
            "unit": "A",
            "reason": "Current exceeds standard safety limits for household/industrial conductors",
        },
    },
    "defaults": {
        "t": 1.0,
    },
}
