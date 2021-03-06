from enum import Enum
from numbers import Number
from typing import Type

from dxbc.Errors import DXBCError


class ScalarType(Enum):
    Untyped = 0

    Float = 1
    Uint = 2
    Hex = 3

    def name(self):
        return {
            ScalarType.Float: "float",
            ScalarType.Uint: "uint",
            ScalarType.Hex: "uint",
            ScalarType.Untyped: "???"
        }[self]

    @staticmethod
    def from_name(name: str) -> 'ScalarType':
        return {
            "float": ScalarType.Float,
            "uint": ScalarType.Uint,
        }[name]

    def __str__(self):
        return self.name()

    def encapsulates(self, other: 'ScalarType'):
        return self.value <= other.value

    def promote_to_existing(self):
        if self == ScalarType.Untyped:
            return ScalarType.Float
        return self

    def format_as_string(self, value):
        if self == ScalarType.Float:
            return f"{value:g}"
        elif self == ScalarType.Uint:
            return f"{value:d}"
        elif self == ScalarType.Hex:
            return hex(value)
        else:
            return str(value)

    @classmethod
    def enum_from_type(cls, type: Type):
        return {
            float: ScalarType.Float,
            int: ScalarType.Uint,
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
