from sympy import symbols, Eq, pi
from families.constants import c

# Define Lidar symbols
Pr, Pt, D_aperture, A_aperture, R, eta_opt, eta_atm, rho_target = symbols(
    "Pr Pt D_aperture A_aperture R eta_opt eta_atm rho_target", positive=True
)
dt, D_footprint, D_beam, theta_div, E_pulse, P_avg, f_rep, tau_pulse = symbols(
    "dt D_footprint D_beam theta_div E_pulse P_avg f_rep tau_pulse", positive=True
)

LIDAR_FAMILY = {
    "name": "lidar",
    "parameters": {
        "Pr": {"description": "Received power", "unit": "W", "dimension": "[mass] * [length]**2 / [time]**3"},
        "Pt": {"description": "Transmitted laser peak power", "unit": "W", "dimension": "[mass] * [length]**2 / [time]**3"},
        "D_aperture": {"description": "Receiver aperture diameter", "unit": "m", "dimension": "[length]"},
        "A_aperture": {"description": "Receiver aperture area", "unit": "m^2", "dimension": "[length]**2"},
        "R": {"description": "Range to target", "unit": "m", "dimension": "[length]"},
        "eta_opt": {"description": "Optical efficiency of transceiver", "unit": "linear", "dimension": "dimensionless"},
        "eta_atm": {"description": "Atmospheric transmission factor", "unit": "linear", "dimension": "dimensionless"},
        "rho_target": {"description": "Target reflectivity", "unit": "linear", "dimension": "dimensionless"},
        "dt": {"description": "Round-trip time of flight", "unit": "s", "dimension": "[time]"},
        "D_footprint": {"description": "Laser footprint diameter at target", "unit": "m", "dimension": "[length]"},
        "D_beam": {"description": "Initial laser beam diameter", "unit": "m", "dimension": "[length]"},
        "theta_div": {"description": "Laser beam divergence angle", "unit": "linear", "dimension": "dimensionless"},
        "E_pulse": {"description": "Laser pulse energy", "unit": "J", "dimension": "[mass] * [length]**2 / [time]**2"},
        "P_avg": {"description": "Average laser power", "unit": "W", "dimension": "[mass] * [length]**2 / [time]**3"},
        "f_rep": {"description": "Pulse repetition frequency", "unit": "Hz", "dimension": "1 / [time]"},
        "tau_pulse": {"description": "Laser pulse width / duration", "unit": "s", "dimension": "[time]"},
    },
    "equations": [
        {
            "name": "aperture_area",
            "equation": Eq(A_aperture, pi * D_aperture**2 / 4),
            "symbol_map": {"A_aperture": A_aperture, "D_aperture": D_aperture},
        },
        {
            "name": "lidar_range_equation",
            "equation": Eq(Pr, Pt * (A_aperture / (pi * R**2)) * eta_opt * eta_atm * rho_target),
            "symbol_map": {
                "Pr": Pr,
                "Pt": Pt,
                "A_aperture": A_aperture,
                "R": R,
                "eta_opt": eta_opt,
                "eta_atm": eta_atm,
                "rho_target": rho_target,
            },
        },
        {
            "name": "lidar_time_of_flight",
            "equation": Eq(R, c * dt / 2),
            "symbol_map": {"R": R, "c": c, "dt": dt},
        },
        {
            "name": "lidar_footprint",
            "equation": Eq(D_footprint, D_beam + R * theta_div),
            "symbol_map": {"D_footprint": D_footprint, "D_beam": D_beam, "R": R, "theta_div": theta_div},
        },
        {
            "name": "pulse_energy",
            "equation": Eq(E_pulse, P_avg / f_rep),
            "symbol_map": {"E_pulse": E_pulse, "P_avg": P_avg, "f_rep": f_rep},
        },
        {
            "name": "peak_power",
            "equation": Eq(Pt, E_pulse / tau_pulse),
            "symbol_map": {"Pt": Pt, "E_pulse": E_pulse, "tau_pulse": tau_pulse},
        },
    ],
    "limits": {
        "eta_opt": {
            "hard_max": 1.0,
            "unit": "linear",
            "reason": "Optical efficiency cannot exceed 1.0 (100%) due to energy conservation",
        },
        "eta_atm": {
            "hard_max": 1.0,
            "unit": "linear",
            "reason": "Atmospheric transmission factor cannot exceed 1.0",
        },
        "rho_target": {
            "hard_max": 1.0,
            "unit": "linear",
            "reason": "Target reflectivity cannot exceed 1.0 (perfect reflector)",
        },
        "theta_div": {
            "soft_max": 0.05,  # 50 mrad
            "unit": "linear",
            "reason": "Beam divergence exceeds typical collimation limits for lidar applications",
        },
    },
    "defaults": {
        "eta_opt": 0.8,
        "eta_atm": 0.9,
        "D_beam": 0.001,  # 1 mm initial beam diameter default
    },
}
