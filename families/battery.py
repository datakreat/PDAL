from sympy import symbols, Eq, log, exp
from families.constants import R_gas, F_const

# Define Battery symbols
I, V, C_rate, Q_cap, P_elec, P_heat, R_int, eta, T, T_limit, d_cooling = symbols(
    "I V C_rate Q_cap P_elec P_heat R_int eta T T_limit d_cooling", positive=True
)
E_spec, Q_spec, E_vol, Q_vol, SoC, SoC_init, t_charge = symbols(
    "E_spec Q_spec E_vol Q_vol SoC SoC_init t_charge", positive=True
)
E_cell, E_standard, n_electrons, Q_rxn, E_act, A_arr, k_rate = symbols(
    "E_cell E_standard n_electrons Q_rxn E_act A_arr k_rate", positive=True
)

BATTERY_FAMILY = {
    "name": "battery",
    "parameters": {
        "I": {"description": "Current", "unit": "A", "dimension": "[current]"},
        "V": {"description": "Voltage", "unit": "V", "dimension": "[mass] * [length]**2 / [time]**3 / [current]"},
        "C_rate": {"description": "C-rate", "unit": "1/hr", "dimension": "1 / [time]"},
        "Q_cap": {"description": "Capacity", "unit": "Ah", "dimension": "[current] * [time]"},
        "P_elec": {"description": "Electrical Power", "unit": "W", "dimension": "[mass] * [length]**2 / [time]**3"},
        "P_heat": {"description": "Heat Dissipation Power", "unit": "W", "dimension": "[mass] * [length]**2 / [time]**3"},
        "R_int": {"description": "Internal Resistance", "unit": "ohm", "dimension": "[mass] * [length]**2 / [time]**3 / [current]**2"},
        "eta": {"description": "Electrochemical Efficiency", "unit": "linear", "dimension": "dimensionless"},
        "T": {"description": "Operating Temperature", "unit": "K", "dimension": "[temperature]"},
        "T_limit": {"description": "Temperature Limit", "unit": "K", "dimension": "[temperature]"},
        "d_cooling": {"description": "Cooling Thickness", "unit": "m", "dimension": "[length]"},
        "E_spec": {"description": "Specific Energy", "unit": "Wh/kg", "dimension": "[length]**2 / [time]**2"},
        "Q_spec": {"description": "Specific Capacity", "unit": "Ah/kg", "dimension": "[current] * [time] / [mass]"},
        "E_vol": {"description": "Volumetric Energy Density", "unit": "Wh/L", "dimension": "[mass] / [length] / [time]**2"},
        "Q_vol": {"description": "Volumetric Capacity Density", "unit": "Ah/L", "dimension": "[current] * [time] / [length]**3"},
        "SoC": {"description": "State of Charge", "unit": "linear", "dimension": "dimensionless"},
        "SoC_init": {"description": "Initial State of Charge", "unit": "linear", "dimension": "dimensionless"},
        "t_charge": {"description": "Charging duration", "unit": "s", "dimension": "[time]"},
        "E_cell": {"description": "Cell Potential / Electromotive Force", "unit": "V", "dimension": "[mass] * [length]**2 / [time]**3 / [current]"},
        "E_standard": {"description": "Standard Cell Potential", "unit": "V", "dimension": "[mass] * [length]**2 / [time]**3 / [current]"},
        "n_electrons": {"description": "Electrons transferred per mole reaction", "unit": "linear", "dimension": "dimensionless"},
        "Q_rxn": {"description": "Reaction quotient", "unit": "linear", "dimension": "dimensionless"},
        "E_act": {"description": "Activation energy", "unit": "J/mol", "dimension": "[mass] * [length]**2 / [time]**2 / [substance]"},
        "A_arr": {"description": "Arrhenius pre-exponential factor", "unit": "1/s", "dimension": "1 / [time]"},
        "k_rate": {"description": "Reaction rate constant", "unit": "1/s", "dimension": "1 / [time]"},
    },
    "equations": [
        {
            "name": "electric_power",
            "equation": Eq(P_elec, V * I),
            "symbol_map": {"P_elec": P_elec, "V": V, "I": I},
        },
        {
            "name": "crate_capacity",
            "equation": Eq(I, C_rate * Q_cap),
            "symbol_map": {"I": I, "C_rate": C_rate, "Q_cap": Q_cap},
        },
        {
            "name": "internal_resistance_heat",
            "equation": Eq(P_heat, I**2 * R_int),
            "symbol_map": {"P_heat": P_heat, "I": I, "R_int": R_int},
        },
        {
            "name": "power_efficiency",
            "equation": Eq(P_heat, P_elec * (1 - eta)),
            "symbol_map": {"P_heat": P_heat, "P_elec": P_elec, "eta": eta},
        },
        {
            "name": "specific_energy",
            "equation": Eq(E_spec, V * Q_spec),
            "symbol_map": {"E_spec": E_spec, "V": V, "Q_spec": Q_spec},
        },
        {
            "name": "volumetric_energy",
            "equation": Eq(E_vol, V * Q_vol),
            "symbol_map": {"E_vol": E_vol, "V": V, "Q_vol": Q_vol},
        },
        {
            "name": "soc_constant_current",
            "equation": Eq(SoC, SoC_init - I * t_charge / Q_cap),
            "symbol_map": {"SoC": SoC, "SoC_init": SoC_init, "I": I, "t_charge": t_charge, "Q_cap": Q_cap},
        },
        {
            "name": "nernst_equation",
            "equation": Eq(E_cell, E_standard - (R_gas * T / (n_electrons * F_const)) * log(Q_rxn)),
            "symbol_map": {
                "E_cell": E_cell,
                "E_standard": E_standard,
                "R_gas": R_gas,
                "T": T,
                "n_electrons": n_electrons,
                "F_const": F_const,
                "Q_rxn": Q_rxn,
            },
        },
        {
            "name": "arrhenius_equation",
            "equation": Eq(k_rate, A_arr * exp(-E_act / (R_gas * T))),
            "symbol_map": {"k_rate": k_rate, "A_arr": A_arr, "E_act": E_act, "R_gas": R_gas, "T": T},
        },
    ],
    "limits": {
        "T_limit": {
            "soft_max": 333.15,  # 60 °C
            "hard_max": 353.15,  # 80 °C
            "unit": "K",
            "reason": "High battery temperature limits lead to accelerated thermal runaway risks",
        },
        "T": {
            "soft_max": 333.15,  # 60 °C
            "hard_max": 353.15,  # 80 °C
            "unit": "K",
            "reason": "Operating temperature exceeds safe limits for lithium-ion electrochemistry",
        },
        "d_cooling": {
            "soft_max": 0.005,  # 5 mm
            "hard_max": 0.010,  # 10 mm
            "unit": "m",
            "reason": "Cooling plate thickness exceeds compact pack constraints",
        },
        "P_heat": {
            "soft_max": 10000.0,  # 10 kW
            "unit": "W",
            "reason": "Required heat dissipation exceeds standard active cooling module capacities",
        },
    },
    "defaults": {
        "R_int": 0.01,  # 10 mOhm default internal resistance
        "SoC_init": 1.0,  # Starts fully charged
        "n_electrons": 1.0,
        "Q_rxn": 1.0,
    },
}
