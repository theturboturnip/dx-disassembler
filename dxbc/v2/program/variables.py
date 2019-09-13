from typing import Optional, Union, List

from dxbc.Errors import DXBCError
from dxbc.v2.Definitions import VectorComponent
from dxbc.v2.Types import ScalarType
from dxbc.v2.values import *


class VariableState:
    name: Optional[ScalarValueBase]
    scalar_type: ScalarType

    def __init__(self, name: Optional[ScalarValueBase], scalar_type: ScalarType):
        self.name = name
        self.scalar_type = scalar_type


class ScalarID:
    """
    The unique name of an assignable scalar value.
    Subscripts are ignored for comparisons and hashing.
    """
    base_name: VarNameBase
    subscript: List[ScalarValueBase]
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
        else:
            raise DXBCError(f"Encountered unknown type {type(base_var)}")

        if isinstance(self.base_name, IndexedVarName):
            self.subscript = self.base_name.indices
            self.base_name = VarNameBase(self.base_name.name)
        else:
            self.subscript = []

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return (self.base_name == other.base_name
                and self.component == other.component)

    def __repr__(self):
        name = str(self.base_name)
        # Ignore subscript
        #if self.subscript:
        #    name = "{}[{}]".format(name, " + ".join(str(x) for x in self.subscript))
        # Can't do `if self.component` here, because VectorComponent.x is 0 and would fail
        if self.component is not None:
            return f"{name}.{self.component.name}"
        return name

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