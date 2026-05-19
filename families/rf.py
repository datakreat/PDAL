from sympy import symbols, Eq, pi
from families.constants import c, k

# Define RF-specific SymPy symbols
Pt, Gt, Gr, lam, R, Pr, T, B, N, SNR, frequency, sigma_rcs, FSPL = symbols(
    "Pt Gt Gr lam R Pr T B N SNR frequency sigma_rcs FSPL", positive=True
)

RF_FAMILY = {
    "name": "rf",
    "parameters": {
        "Pt": {"description": "Transmit power", "unit": "W", "dimension": "[mass] * [length]**2 / [time]**3"},
        "frequency": {"description": "Carrier frequency", "unit": "Hz", "dimension": "1 / [time]"},
        "lam": {"description": "Wavelength", "unit": "m", "dimension": "[length]"},
        "R": {"description": "Range", "unit": "m", "dimension": "[length]"},
        "Gt": {"description": "Transmit antenna gain", "unit": "linear", "dimension": "dimensionless"},
        "Gr": {"description": "Receive antenna gain", "unit": "linear", "dimension": "dimensionless"},
        "B": {"description": "Bandwidth", "unit": "Hz", "dimension": "1 / [time]"},
        "T": {"description": "Noise temperature", "unit": "K", "dimension": "[temperature]"},
        "N": {"description": "Thermal noise power", "unit": "W", "dimension": "[mass] * [length]**2 / [time]**3"},
        "Pr": {"description": "Received power", "unit": "W", "dimension": "[mass] * [length]**2 / [time]**3"},
        "SNR": {"description": "Signal-to-noise ratio", "unit": "linear", "dimension": "dimensionless"},
        "sigma_rcs": {"description": "Radar cross section", "unit": "m^2", "dimension": "[length]**2"},
        "FSPL": {"description": "Free space path loss", "unit": "linear", "dimension": "dimensionless"},
    },
    "equations": [
        {
            "name": "thermal_noise",
            "equation": Eq(N, k * T * B),
            "symbol_map": {"N": N, "k": k, "T": T, "B": B},
        },
        {
            "name": "wavelength",
            "equation": Eq(lam, c / frequency),
            "symbol_map": {"lam": lam, "c": c, "frequency": frequency},
        },
        {
            "name": "friis",
            "equation": Eq(Pr, Pt * Gt * Gr * (lam / (4 * pi * R)) ** 2),
            "symbol_map": {"Pt": Pt, "Gt": Gt, "Gr": Gr, "lam": lam, "R": R, "Pr": Pr},
        },
        {
            "name": "snr",
            "equation": Eq(SNR, Pr / N),
            "symbol_map": {"SNR": SNR, "Pr": Pr, "N": N},
        },
        {
            "name": "radar_range_equation",
            "equation": Eq(Pr, Pt * Gt * Gr * (lam**2) * sigma_rcs / ((4 * pi)**3 * R**4)),
            "symbol_map": {"Pt": Pt, "Gt": Gt, "Gr": Gr, "lam": lam, "R": R, "Pr": Pr, "sigma_rcs": sigma_rcs},
        },
        {
            "name": "free_space_path_loss",
            "equation": Eq(FSPL, (4 * pi * R / lam)**2),
            "symbol_map": {"FSPL": FSPL, "R": R, "lam": lam},
        },
    ],
    "limits": {
        "Pt": {
            "soft_max": 100.0,
            "hard_max": 10000.0,
            "unit": "W",
            "reason": "Required transmit power exceeds practical/physical engineering bounds",
        },
        "frequency": {
            "hard_max": 100e9,
            "unit": "Hz",
            "reason": "Carrier frequency exceeds experimental sub-terahertz limits",
        },
    },
    "defaults": {
        "Gt": 3.16,
        "Gr": 3.16,
        "B": 1e6,
        "T": 290,
    },
}
