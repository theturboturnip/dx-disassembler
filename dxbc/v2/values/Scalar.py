import copy

from dxbc.Errors import DXBCError
from dxbc.v2.Types import ScalarType
from dxbc.v2.Definitions import VectorComponent
from dxbc.v2.values import ScalarValueBase, VarNameBase


"""class CastedScalar(ScalarValueBase):
    origin_scalar: ScalarValueBase

    def __init__(self, origin_scalar: ScalarValueBase, casted_type: ScalarType):
        if casted_type == ScalarType.Untyped:
            raise DXBCError("Can't cast to Untyped")
        super().__init__(casted_type, False, assignable=origin_scalar.assignable)
        self.origin_scalar = origin_scalar

    def __repr__(self):
        return f"CastedScalar {self.scalar_type} of ({self.origin_scalar})"

    def __str__(self):
        if self.scalar_type == self.origin_scalar.scalar_type or self.origin_scalar.scalar_type == ScalarType.Untyped:
            return str(self.origin_scalar)
        return f"({self.scalar_type.name()}){str(self.origin_scalar)}"
"""
def cast_scalar(scalar: ScalarValueBase, scalar_type: ScalarType) -> ScalarValueBase:
    scalar = copy.copy(scalar)
    scalar.scalar_type = scalar_type
    return scalar


class ImmediateScalar(ScalarValueBase):
    def __init__(self, value, scalar_type: ScalarType, negated: bool):
        if value < 0:
            raise DXBCError("Can't have negative immediates, convert to positive form and use `negated` instead.")
        # You can't assign a value to an immediate
        super().__init__(scalar_type, negated, assignable=False)
        self.value = value

    def __eq__(self, other):
        return (super().__eq__(other)
                and self.value == other.value)

    def __repr__(self):
        return f"ImmediateScalar {self.scalar_type} {self.negated} {self.value}"

    def __str__(self):
        return "{}{}".format("-" if self.negated else "", self.scalar_type.format_as_string(self.value))


class ScalarVariable(ScalarValueBase):
    scalar_name: VarNameBase

    def __init__(self, var_name: VarNameBase, scalar_type: ScalarType, negated: bool):
        super().__init__(scalar_type, negated, assignable=True)
        self.scalar_name = var_name

    def __eq__(self, other):
        return (super().__eq__(other)
                and self.scalar_name == other.scalar_name)

    def __repr__(self):
        return f"ScalarVariable {self.scalar_type} {self.negated} {self.scalar_name} w:{self.assignable} d:{self.num_components}"

    def __str__(self):
        return "{}{}".format("-" if self.negated else "", self.scalar_name)


class SingleVectorComponent(ScalarValueBase):
    vector_name: VarNameBase
    component_name: VectorComponent

    def __init__(self, vector_name: VarNameBase, component_name: VectorComponent, scalar_type: ScalarType, negated: bool):
        # Vector components are always assignable
        super().__init__(scalar_type, negated, assignable=True)
        self.vector_name = vector_name
        self.component_name = component_name

    def __eq__(self, other):
        return (super().__eq__(other)
                and self.vector_name == other.vector_name
                and self.component_name == other.component_name)

    def __repr__(self):
        return f"SingleVectorComponent {self.scalar_type} {self.negated} {self.vector_name}.{self.component_name.name}"

    def __str__(self):
        return "{}{}.{}".format("-" if self.negated else "", self.vector_name, self.component_name.name)