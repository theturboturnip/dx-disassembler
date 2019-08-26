from enum import Enum
from numbers import Number
from typing import Type

from dxbc.Errors import DXBCError


class ScalarType(Enum):
    Untyped = -1

    Float = 0
    Int = 1
    Hex = 2

    def name(self):
        return {
            ScalarType.Float: "float",
            ScalarType.Int: "int",
            ScalarType.Hex: "int",
            ScalarType.Untyped: "???"
        }[self]

    def __str__(self):
        return self.name()

    def encapsulates(self, other: 'ScalarType'):
        return self.value <= other.value

    def format_as_string(self, value):
        if self == ScalarType.Float:
            return f"{value:f}"
        elif self == ScalarType.Int:
            return f"{value:d}"
        elif self == ScalarType.Hex:
            return hex(value)
        else:
            return str(value)

    @classmethod
    def enum_from_type(cls, type: Type):
        return {
            float: ScalarType.Float,
            int: ScalarType.Int,
        }[type]


class VectorType:
    scalar_type: ScalarType
    count: int

    def __init__(self, scalar_type: ScalarType, count: int):
        if count < 2:
            raise DXBCError("Can't create a VectorType with <2 components!")
        if count > 4:
            raise DXBCError("Can't create a VectorType with >4 components!")
        self.scalar_type = scalar_type
        self.count = count

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return (self.scalar_type == other.scalar_type
                and self.count == other.count)

    def __repr__(self):
        return f"{self.scalar_type}{self.count}"
    def __str__(self):
        return repr(self)

def get_least_permissive_container_type(*types: ScalarType) -> ScalarType:
    current_type = types[0]
    for new_type in types[1:]:
        if new_type.encapsulates(current_type):
            current_type = new_type
    return current_type