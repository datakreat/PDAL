from sympy import symbols, Eq

c, k, g, R_gas, F_const, G_grav = symbols("c k g R_gas F_const G_grav", positive=True)

# Register constants as equations in SymPy format
CONSTANTS_REGISTRY = [
    {
        "name": "speed_of_light",
        "equation": Eq(c, 3e8),
        "symbol_map": {"c": c},
    },
    {
        "name": "boltzmann_constant",
        "equation": Eq(k, 1.380649e-23),
        "symbol_map": {"k": k},
    },
    {
        "name": "acceleration_of_gravity",
        "equation": Eq(g, 9.81),
        "symbol_map": {"g": g},
    },
    {
        "name": "gas_constant",
        "equation": Eq(R_gas, 8.314462618),
        "symbol_map": {"R_gas": R_gas},
    },
    {
        "name": "faraday_constant",
        "equation": Eq(F_const, 96485.332),
        "symbol_map": {"F_const": F_const},
    },
    {
        "name": "gravitational_constant",
        "equation": Eq(G_grav, 6.6743e-11),
        "symbol_map": {"G_grav": G_grav},
    },
]


