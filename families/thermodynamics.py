from sympy import symbols, Eq
from families.constants import R_gas

# Define Thermodynamics symbols
P, V, n, T, Q, m, c_sp, dT = symbols("P V n T Q m c_sp dT", positive=True)
rho_gas, M_molar, Q_cond, k_thermal, A_cond, d_cond = symbols(
    "rho_gas M_molar Q_cond k_thermal A_cond d_cond", positive=True
)

THERMODYNAMICS_FAMILY = {
    "name": "thermodynamics",
    "parameters": {
        "P": {"description": "Pressure", "unit": "Pa", "dimension": "[mass] / [length] / [time]**2"},
        "V": {"description": "Volume", "unit": "m^3", "dimension": "[length]**3"},
        "n": {"description": "Moles", "unit": "mol", "dimension": "[substance]"},
        "T": {"description": "Temperature", "unit": "K", "dimension": "[temperature]"},
        "Q": {"description": "Heat Energy", "unit": "J", "dimension": "[mass] * [length]**2 / [time]**2"},
        "m": {"description": "Mass", "unit": "kg", "dimension": "[mass]"},
        "c_sp": {"description": "Specific Heat", "unit": "J/(kg*K)", "dimension": "[length]**2 / [time]**2 / [temperature]"},
        "dT": {"description": "Temperature Difference", "unit": "K", "dimension": "[temperature]"},
        "rho_gas": {"description": "Gas Density", "unit": "kg/m^3", "dimension": "[mass] / [length]**3"},
        "M_molar": {"description": "Molar Mass", "unit": "kg/mol", "dimension": "[mass] / [substance]"},
        "Q_cond": {"description": "Conduction Heat Rate", "unit": "W", "dimension": "[mass] * [length]**2 / [time]**3"},
        "k_thermal": {"description": "Thermal Conductivity", "unit": "W/(m*K)", "dimension": "[mass] * [length] / [time]**3 / [temperature]"},
        "A_cond": {"description": "Conduction Area", "unit": "m^2", "dimension": "[length]**2"},
        "d_cond": {"description": "Conduction Thickness", "unit": "m", "dimension": "[length]"},
    },
    "equations": [
        {
            "name": "ideal_gas_law",
            "equation": Eq(P * V, n * R_gas * T),
            "symbol_map": {"P": P, "V": V, "n": n, "R_gas": R_gas, "T": T},
        },
        {
            "name": "heat_energy",
            "equation": Eq(Q, m * c_sp * dT),
            "symbol_map": {"Q": Q, "m": m, "c_sp": c_sp, "dT": dT},
        },
        {
            "name": "gas_density",
            "equation": Eq(rho_gas, P * M_molar / (R_gas * T)),
            "symbol_map": {"rho_gas": rho_gas, "P": P, "M_molar": M_molar, "R_gas": R_gas, "T": T},
        },
        {
            "name": "thermal_conduction",
            "equation": Eq(Q_cond, k_thermal * A_cond * dT / d_cond),
            "symbol_map": {"Q_cond": Q_cond, "k_thermal": k_thermal, "A_cond": A_cond, "dT": dT, "d_cond": d_cond},
        },
    ],
    "limits": {
        "T": {
            "soft_max": 2000.0,
            "hard_max": 5000.0,
            "unit": "K",
            "reason": "Temperature exceeds practical structural limits for most engineering materials",
        },
        "P": {
            "soft_max": 1.0e8,
            "unit": "Pa",
            "reason": "Pressure exceeds standard high-pressure vessel safety levels",
        },
    },
    "defaults": {
        "n": 1.0,
        "c_sp": 4184.0,  # Specific heat capacity of water J/(kg*K)
    },
}
