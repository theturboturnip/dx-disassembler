from typing import List, cast, Tuple

from dxbc.Errors import DXBCError
from dxbc.v2.values import VarNames
from dxbc.v2.values import VectorValueBase, ScalarValueBase
from dxbc.v2.values import SingleVectorComponent
from utils import FirstPossibleOf


class UnnamedVectorValue(VectorValueBase):
    """
    A vector value created from multiple origins.
    """
    def get_output_mask(self) -> Tuple[bool, bool, bool, bool]:
        # This will always return Tuple of 4 bools, the static checker can't tell
        return tuple([True] * self.num_components + [False] * (4 - self.num_components))

    def __repr__(self):
        return "UnnamedVectorValue {} {} {} r/w:{}".format(self.scalar_type.name(), self.negated, ", ".join(repr(x) for x in self.scalar_values), self.assignable)

    def disassemble(self, type_length: int = -1):
        if all(x == self.scalar_values[0] for x in self.scalar_values):
            return "{}{}".format("-" if self.negated else "", self.scalar_values[0])
        return "{}{}{}({})".format("-" if self.negated else "", self.scalar_type.name(), self.num_components, ", ".join(str(x) for x in self.scalar_values))


class SwizzledVectorValue(VectorValueBase):
    """
    A vector value created from components of a single named vector.
    """
    vector_name: VarNames

    def __init__(self, scalar_values: List[ScalarValueBase], negated: bool):
        vector_name = None
        for v in scalar_values:
            if not isinstance(v, SingleVectorComponent):
                raise DXBCError("Tried to create a SwizzledVectorValue with a component that didn't come from a vector")
            if vector_name is None:
                vector_name = v.vector_name
            elif vector_name != v.vector_name:
                raise DXBCError("Tried to create a SwizzledVectorValue with components that didn't come from the same "
                                "vector")
            if v.negated:
                # TODO We should be able to detect when a vector has all components negated and not throw
                raise DXBCError("Tried to create a SwizzledVectorValue with a negated component")
        super().__init__(scalar_values, negated)
        self.vector_name = vector_name
        self.components = [cast(SingleVectorComponent, x).component_name for x in scalar_values]

    def __eq__(self, other):
        return (super().__eq__(other)
                and self.vector_name == other.vector_name
                and self.components == other.components)

    def get_output_mask(self) -> Tuple[bool, bool, bool, bool]:
        # This will always return Tuple of 4 bools, the static checker can't tell
        mask = [False] * 4
        for comp in self.components:
            mask[comp] = True
        return tuple(mask)

    def __repr__(self):
        return "{}{}.{}".format("-" if self.negated else "", self.vector_name, "".join([x.name for x in self.components]))

    def disassemble(self, type_length: int = -1):
        if type_length == self.num_components:
            if all(x == i for i, x in enumerate(self.components)):
                return "{}{}".format("-" if self.negated else "", self.vector_name)
        if all(x == self.components[0] for x in self.components):
            return "{}{}.{}".format("-" if self.negated else "", self.vector_name, self.components[0].name)
        return repr(self)


# When created, will return a SwizzledVectorValue if all arguments come from the same named vector.
# Otherwise, will return a NewVectorValue.
VectorValue = FirstPossibleOf([SwizzledVectorValue, UnnamedVectorValue])
