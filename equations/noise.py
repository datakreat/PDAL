from sympy import symbols, Eq

k = 1.380649e-23

T, B, N = symbols(
    "T B N",
    positive=True
)

noise_equation = Eq(
    N,
    k * T * B
)

NOISE_METADATA = {
    "name": "thermal_noise",
    "inputs": ["T", "B"],
    "outputs": ["N"],
    "equation": noise_equation,

    "symbol_map": {
        "T": T,
        "B": B,
        "N": N
    }
}