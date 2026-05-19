from families.constants import CONSTANTS_REGISTRY
from families.rf import RF_FAMILY
from families.kinematics import KINEMATICS_FAMILY
from families.dynamics import DYNAMICS_FAMILY
from families.circuits import CIRCUITS_FAMILY
from families.thermodynamics import THERMODYNAMICS_FAMILY
from families.battery import BATTERY_FAMILY
from families.aerospace import AEROSPACE_FAMILY
from families.lidar import LIDAR_FAMILY

FAMILIES = {
    "rf": RF_FAMILY,
    "kinematics": KINEMATICS_FAMILY,
    "dynamics": DYNAMICS_FAMILY,
    "circuits": CIRCUITS_FAMILY,
    "thermodynamics": THERMODYNAMICS_FAMILY,
    "battery": BATTERY_FAMILY,
    "aerospace": AEROSPACE_FAMILY,
    "lidar": LIDAR_FAMILY,
}




def get_family_registry(family_name: str) -> list:
    """
    Returns a unified registry of equations (constants + family-specific formulas)
    to solve queries inside the selected physics family.
    """
    if family_name not in FAMILIES:
        raise ValueError(f"Unknown physics family: {family_name}")

    family = FAMILIES[family_name]

    # Combine global physical constants and family-specific equations
    registry = []
    registry.extend(CONSTANTS_REGISTRY)
    registry.extend(family["equations"])

    return registry
