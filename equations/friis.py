from sympy import symbols, Eq, pi

Pt, Gt, Gr, lam, R, Pr = symbols(
    "Pt Gt Gr lam R Pr",
    positive=True
)

friis_equation = Eq(
    Pr,
    Pt * Gt * Gr * (lam / (4 * pi * R))**2
)

FRIIS_METADATA = {
    "name": "friis",
    "inputs": ["Pt", "Gt", "Gr", "lam", "R"],
    "outputs": ["Pr"],
    "equation": friis_equation,
    "symbol_map": {
        "Pt": Pt,
        "Gt": Gt,
        "Gr": Gr,
        "lam": lam,
        "R": R,
        "Pr": Pr
    }
}
FRIIS_INVERSE_METADATA = {

    "name": "friis_inverse_pt",

    "inputs": [
        "Pr",
        "Gt",
        "Gr",
        "lam",
        "R"
    ],

    "outputs": ["Pt"],

    "equation": friis_equation,

    "symbol_map": {
        "Pt": Pt,
        "Gt": Gt,
        "Gr": Gr,
        "lam": lam,
        "R": R,
        "Pr": Pr
    }
}