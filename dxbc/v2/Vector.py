from typing import List, cast

from dxbc.Errors import DXBCError
from dxbc.v2 import VarNames
from dxbc.v2.Base import VectorValueBase, ScalarValueBase
from dxbc.v2.Scalar import SingleVectorComponent
from utils import FirstPossibleOf


class UnnamedVectorValue(VectorValueBase):
    """
    A vector value created from multiple origins.
    """

    def __repr__(self):
        return "UnnamedVectorValue {} {} {} r/w:{}".format(str(self.value_type), self.negated, ", ".join(repr(x) for x in self.scalar_values), self.assignable)

    def __str__(self):
        return "-{}{}({})".format("-" if self.negated else "", str(self.value_type), self.num_components, ", ".join(str(x) for x in self.scalar_values))

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

    def __repr__(self):
        return "{}{}.{}".format("-" if self.negated else "", self.vector_name, "".join([x.name for x in self.components]))
    def __str__(self):
        return repr(self)

# When created, will return a SwizzledVectorValue if all arguments come from the same named vector.
# Otherwise, will return a NewVectorValue.
VectorValue = FirstPossibleOf([SwizzledVectorValue, UnnamedVectorValue])


def trim_components(vec: VectorValueBase, component_count: int) -> VectorValueBase:
    new_components = vec.scalar_values
    if len(new_components) < component_count or component_count <= 0:
        raise DXBCError("Invalid argument to trim_components, tried to trim vector with {} comps to {}".format(
            len(new_components), component_count))

    # Promote to SwizzledVectorValue if possible
    # (in case something like (a.x, a.y, a.z, 1.0) is trimmed to 3 components)
    return VectorValue(new_components[0:component_count])