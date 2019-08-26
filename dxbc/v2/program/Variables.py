from typing import Optional, Union, List

from dxbc.Errors import DXBCError
from dxbc.v2.Definitions import VectorComponent
from dxbc.v2.Types import ScalarType
from dxbc.v2.values import *


class VariableState:
    last_modified: int
    scalar_type: ScalarType

    # TODO Shouldn't let scalar_type be defaulted
    def __init__(self, last_modified: int, scalar_type: ScalarType = ScalarType.Untyped):
        self.last_modified = last_modified
        self.scalar_type = scalar_type


class ScalarID:
    base_name: VarNameBase
    component: Optional[VectorComponent]

    def __init__(self, base_var: Union[ScalarValueBase, VarNameBase], component: Optional[VectorComponent] = None):
        if isinstance(base_var, ImmediateScalar):
            raise DXBCError("Can't refer to an immediate with an ID!")
        elif isinstance(base_var, SingleVectorComponent):
            self.base_name = base_var.vector_name
            self.component = base_var.component_name
        elif isinstance(base_var, ScalarVariable):
            self.base_name = base_var.scalar_name
            self.component = None
        elif isinstance(base_var, VarNameBase):
            self.base_name = base_var
            self.component = component

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return (self.base_name == other.base_name
                and self.component == other.component)

    def __repr__(self):
        # Can't do `if self.component` here, because VectorComponent.x is 0 and would fail
        if self.component is not None:
            return f"{self.base_name}.{self.component.name}"
        return f"{self.base_name}"

    def __hash__(self):
        # Quick and dirty hash
        return hash(repr(self))


class VectorID:
    base_name: VarNameBase
    components: List[VectorComponent]

    def __init__(self, base_var: VectorValueBase):
        if isinstance(base_var, UnnamedVectorValue):
            raise DXBCError("Can't refer to an unnamed vector with an ID!")
        elif isinstance(base_var, SwizzledVectorValue):
            self.base_name = base_var.vector_name
            self.components = base_var.components

    def __repr__(self):
        return "{}.{}".format(self.base_name, "".join(x.name for x in self.components))

    def __hash__(self):
        return hash(repr(self))

def get_scalar_ids(value: Value) -> List[ScalarID]:
    if isinstance(value, ScalarValueBase):
        try:
            return [ScalarID(value)]
        except DXBCError:
            return []
    elif isinstance(value, VectorValueBase):
        ids = []
        for component_value in value.scalar_values:
            try:
                ids.append(ScalarID(component_value))
            except DXBCError:
                pass
        return ids
    raise DXBCError(f"get_scalar_ids doesn't know how to handle objects of type {type(value)}")