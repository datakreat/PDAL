from pydantic import BaseModel
from typing import Optional


class Parameter(BaseModel):
    name: str
    value: float
    unit: str
    source: str = "user"


class DerivedParameter(Parameter):
    equation: str