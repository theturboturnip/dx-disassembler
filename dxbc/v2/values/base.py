from abc import ABC
from typing import List, Tuple, Optional

from dxbc.Errors import DXBCError
from dxbc.v2.Types import get_least_permissive_container_type, ScalarType


class Value:
    """
    Value with one or more components, all of the same type.
    """

    num_components: int
    scalar_type: ScalarType
    negated: bool
    assignable: bool

    def __init__(self, component_types: List[ScalarType], negated: bool, assignable: bool):
        """
        Inits the Value based on the types of each component.
        The type of the Value is the least permissive type that every
        component type can be converted to without losing data.

        :param component_types: The types of each component.
        """
        self.num_components = len(component_types)
        self.scalar_type = get_least_permissive_container_type(*component_types)
        self.negated = negated
        self.assignable = assignable

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False

        return (self.num_components == other.num_components
                and self.scalar_type == other.scalar_type
                and self.negated == other.negated
                and self.assignable == other.assignable)

    def get_output_mask(self) -> Tuple[bool, bool, bool, bool]:
        raise NotImplementedError()

    def disassemble(self, type_length: int = -1) -> str:
        raise NotImplementedError()

    def __str__(self):
        return self.disassemble()


class ScalarValueBase(Value):
    def __init__(self, scalar_type: ScalarType, negated: bool, assignable: bool):
        super().__init__([scalar_type], negated, assignable)

    def get_output_mask(self) -> Tuple[bool, bool, bool, bool]:
        return (True, False, False, False)


class VectorValueBase(Value, ABC):
    scalar_values: List[ScalarValueBase]

    def __init__(self, scalar_values: List[ScalarValueBase], negated: bool):
        scalar_values = list(scalar_values)
        if not all(isinstance(x, ScalarValueBase) for x in scalar_values):
            raise DXBCError("Tried to make a Vector with non-scalar components!")
        if len(scalar_values) > 4:
            raise DXBCError("Tried to make a Vector with >4 values")
        if len(scalar_values) < 2:
            raise DXBCError("Tried to make a Vector with <2 values")
        super().__init__([x.scalar_type for x in scalar_values], negated, all(x.assignable for x in scalar_values))
        self.scalar_values = scalar_values

    def __eq__(self, other):
        return (super().__eq__(other)
                and self.scalar_values == other.scalar_values)


