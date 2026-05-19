from pint import UnitRegistry

ureg = UnitRegistry()


def to_base(value: float, unit: str):
    q = value * ureg(unit)
    return q.to_base_units()


def convert(value: float, from_unit: str, to_unit: str):
    q = value * ureg(from_unit)
    return q.to(to_unit)