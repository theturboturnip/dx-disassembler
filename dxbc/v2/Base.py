from enum import Enum
from typing import List, Type

from dxbc.Errors import DXBCError


class Untyped:
    pass

# Lists types from most permissive to least.
# i.e. a float cannot be converted to an int without losing data, so it appears before int.
type_hierarchy = [
    float,
    int,
    hex,
    Untyped,
]


def get_least_permissive_container_type(*types: [type]) -> type:
    current_type = types[0]
    for new_type in types[1:]:
        for t in type_hierarchy:
            if t in [new_type, current_type]:
                current_type = t
    return current_type


class Value:
    """
    Value with one or more components, all of the same type.
    """

    num_components: int
    value_type: type
    negated: bool
    assignable: bool

    def __init__(self, component_types: List[Type], negated: bool, assignable: bool):
        """
        Inits the Value based on the types of each component.
        The type of the Value is the least permissive type that every
        component type can be converted to without losing data.

        :param component_types: The types of each component.
        """
        self.num_components = len(component_types)
        self.value_type = get_least_permissive_container_type(*component_types)
        self.negated = negated
        self.assignable = assignable

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False

        return (self.num_components == other.num_components
                and self.value_type == other.value_type
                and self.negated == other.negated
                and self.assignable == other.assignable)


class ScalarValueBase(Value):
    def __init__(self, scalar_type: type, negated: bool, assignable: bool):
        super().__init__([scalar_type], negated, assignable)


class VectorValueBase(Value):
    scalar_values: List[ScalarValueBase]

    def __init__(self, scalar_values: List[ScalarValueBase], negated: bool):
        scalar_values = list(scalar_values)
        if not all(isinstance(x, ScalarValueBase) for x in scalar_values):
            raise DXBCError("Tried to make a Vector with non-scalar components!")
        super().__init__([x.value_type for x in scalar_values], negated, all([x.assignable for x in scalar_values]))
        self.scalar_values = scalar_values

    def __eq__(self, other):
        return (super().__eq__(other)
                and self.scalar_values == other.scalar_values)


class VectorComponent(Enum):
    x = 0
    y = 1
    z = 2
    w = 3
    r = x
    g = y
    b = z
    a = w