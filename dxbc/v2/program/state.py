from typing import Dict, Optional

from dxbc.v2.Types import ScalarType
from dxbc.v2.program.variables import *
from dxbc.v2.values.scalar import cast_scalar
from utils import dict_str


class ExecutionState:
    state_map: Dict[ScalarID, VariableState]
    vector_map: Dict[VarNameBase, int]

    def __init__(self, state_map: Dict[ScalarID, VariableState] = None, vector_map: Dict[VarNameBase, int] = None):
        self.state_map = state_map if state_map is not None else {}
        self.vector_map = vector_map if vector_map is not None else {}

    def copy(self):
        return ExecutionState(self.state_map.copy(), self.vector_map.copy())

    def get_type_for_either_name(self, name: VarNameBase):
        name = name.as_base()
        if name in self.vector_map:
            return self.get_type(ScalarID(name, VectorComponent.x))
        else:
            return self.get_type(ScalarID(name))

    def get_type(self, scalar_id: ScalarID, default: Optional[ScalarType] = ScalarType.Untyped) -> Optional[ScalarType]:
        var_state = self.state_map.get(scalar_id, None)
        if var_state is None:
            return default
        return var_state.scalar_type

    def get_vector_length(self, var: Value, default:int = -1) -> int:
        if hasattr(var, "vector_name"):
            return self.vector_map[var.vector_name.as_base()]
        return default

    def get_name(self, scalar_id: ScalarID, default: ScalarValueBase) -> ScalarValueBase:
        var_state = self.state_map.get(scalar_id, None)
        if var_state is None or var_state.name is None:
            return default
        return var_state.name

    def set_scalar_map(self, scalar_id: ScalarID, name: ScalarValueBase, scalar_type: ScalarType):
        self.state_map[scalar_id] = VariableState(name, scalar_type)

    def set_vector_map(self, var_name: VarNameBase, output_ids: List[ScalarID], output_scalar_type: ScalarType):
        for (i, output_id) in enumerate(output_ids):
            self.set_scalar_map(
                output_id,
                SingleVectorComponent(var_name, VectorComponent(i), output_scalar_type, False),
                output_scalar_type
            )
        self.set_vector_length(var_name, len(output_ids))

    def set_vector_length(self, name: VarNameBase, count: int):
        self.vector_map[name] = count

    def infer_and_cast_type(self, value: Value) -> Value:
        if value.scalar_type is not ScalarType.Untyped:
            return value

        if isinstance(value, ScalarValueBase):
            val_id = ScalarID(value)
            variable_type = self.get_type(val_id, default=None)
            if not variable_type:
                raise DXBCError(f"Variable for value {value} has no state, can't infer type")
            if variable_type == ScalarType.Untyped:
                # This type has been set to untyped, assume there's a reason and just pass it through
                # This is for things like Samplers and Textures which we don't care about for typing purposes
                return value
            new_type = variable_type
            return cast_scalar(value, new_type)
        elif isinstance(value, VectorValueBase):
            return VectorValue([self.infer_and_cast_type(c) for c in value.scalar_values], value.negated)