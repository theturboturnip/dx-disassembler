import difflib

from dxbc.Errors import DXBCError
from dxbc.v2 import VarNames
from dxbc.v2.Base import ScalarValueBase, VectorComponent
from dxbc.v2.VarNames import VarNameBase


class ImmediateScalar(ScalarValueBase):
    def __init__(self, value, scalar_type: type, negated: bool):
        if value < 0:
            raise DXBCError("Can't have negative immediates, convert to positive form and use `negated` instead.")
        # You can't assign a value to an immediate
        super().__init__(scalar_type, negated, False)
        self.value = value

    def __eq__(self, other):
        return (super().__eq__(other)
                and self.value == other.value)

    def __repr__(self):
        return f"ImmediateScalar {self.value_type} {self.negated} {self.value}"

    def __str__(self):
        return "{}{}".format("-" if self.negated else "", self.value)


class ScalarVariable(ScalarValueBase):
    scalar_name: VarNameBase

    def __init__(self, var_name: VarNameBase, scalar_type: type, negated: bool):
        super().__init__(scalar_type, negated, True)
        self.scalar_name = var_name

    def __eq__(self, other):
        return (super().__eq__(other)
                and self.scalar_name == other.scalar_name)

    def __repr__(self):
        return f"ScalarVariable {self.value_type} {self.negated} {self.scalar_name} w:{self.assignable} d:{self.num_components}"

    def __str__(self):
        return "{}{}".format("-" if self.negated else "", self.scalar_name)


class SingleVectorComponent(ScalarValueBase):
    vector_name: VarNameBase
    component_name: VectorComponent

    def __init__(self, vector_name: VarNameBase, component_name: VectorComponent, component_type, negated: bool):
        # Vector components are always assignable
        super().__init__(component_type, negated, True)
        self.vector_name = vector_name
        self.component_name = component_name

    def __eq__(self, other):
        return (super().__eq__(other)
                and self.vector_name == other.vector_name
                and self.component_name == other.component_name)

    def __repr__(self):
        return f"SingleVectorComponent {self.value_type} {self.negated} {self.vector_name}.{self.component_name.name}"

    def __str__(self):
        return "{}{}.{}".format("-" if self.negated else "", self.vector_name, self.component_name.name)
