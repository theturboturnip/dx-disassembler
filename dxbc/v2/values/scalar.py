import copy
import types
from typing import Tuple

from dxbc.Errors import DXBCError
from dxbc.v2.types import ScalarType
from dxbc.v2.definitions import VectorComponent
from dxbc.v2.values import ScalarValueBase, VarNameBase

def cast_scalar(scalar: ScalarValueBase, scalar_type: ScalarType) -> ScalarValueBase:
    scalar = copy.copy(scalar)
    scalar.scalar_type = scalar_type
    return scalar

def reinterpret_scalar(scalar: ScalarValueBase, scalar_type: ScalarType) -> ScalarValueBase:
    if scalar.scalar_type == scalar_type:
        return scalar
    scalar = copy.copy(scalar)
    scalar.scalar_type = scalar_type
    old_str = scalar.__str__
    scalar.__class__ = type(f"reinterpreted{scalar.__class__.__name__}",
                            (scalar.__class__,),
                            {
                                "__str__": lambda self: f"{scalar_type.name()}({old_str()})"
                            })
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

    def disassemble(self, type_length: int = -1):
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
        return f"ScalarVariable {self.scalar_type} {self.negated} {self.scalar_name} w:{self.named} d:{self.num_components}"

    def disassemble(self, type_length: int = -1):
        return "{}{}".format("-" if self.negated else "", self.scalar_name)

    def get_var_name(self) -> VarNameBase:
        return self.scalar_name

    def set_var_name(self, new_name: VarNameBase):
        self.scalar_name = new_name

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

    def get_output_mask(self) -> Tuple[bool, bool, bool, bool]:
        return (self.component_name == VectorComponent.x,
                self.component_name == VectorComponent.y,
                self.component_name == VectorComponent.z,
                self.component_name == VectorComponent.w)

    def get_var_name(self) -> VarNameBase:
        return self.vector_name
    def set_var_name(self, new_name: VarNameBase):
        self.vector_name = new_name

    def get_component_str(self):
        return self.component_name.name

    def disassemble(self, type_length: int = -1):
        return "{}{}.{}".format("-" if self.negated else "", self.vector_name, self.component_name.name)
