from sympy import symbols, Eq

Pr, N, SNR = symbols(
    "Pr N SNR",
    positive=True
)

snr_equation = Eq(
    SNR,
    Pr / N
)

SNR_METADATA = {
    "name": "snr",
    "inputs": ["Pr", "N"],
    "outputs": ["SNR"],
    "equation": snr_equation
}