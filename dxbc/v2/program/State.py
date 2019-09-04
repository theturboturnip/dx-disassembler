from typing import Dict, Optional

from dxbc.v2.Types import ScalarType
from dxbc.v2.program.Variables import ScalarID, VariableState, ScalarValueBase, VarNameBase, SwizzledVectorValue, Value
from utils import dict_str


class ProgramState:
    state_map: Dict[ScalarID, VariableState]
    vector_map: Dict[VarNameBase, int]

    def __init__(self, state_map: Dict[ScalarID, VariableState] = None, vector_map: Dict[VarNameBase, int] = None):
        self.state_map = state_map if state_map is not None else {}
        self.vector_map = vector_map if vector_map is not None else {}

    def copy(self):
        return ProgramState(self.state_map.copy(), self.vector_map.copy())

    def get_type(self, scalar_id: ScalarID, default: Optional[ScalarType] = ScalarType.Untyped) -> Optional[ScalarType]:
        var_state = self.state_map.get(scalar_id, None)
        if var_state is None:
            return default
        return var_state.scalar_type

    def get_vector_length(self, var: Value) -> int:
        if isinstance(var, SwizzledVectorValue):
            return self.vector_map[var.vector_name.as_base()]
        return -1

    def get_name(self, scalar_id: ScalarID, default: ScalarValueBase) -> ScalarValueBase:
        var_state = self.state_map.get(scalar_id, None)
        if var_state is None or var_state.name is None:
            return default
        return var_state.name

    def set_scalar_map(self, scalar_id: ScalarID, name: ScalarValueBase, scalar_type: ScalarType):
        self.state_map[scalar_id] = VariableState(name, scalar_type)

    def set_vector_length(self, name: VarNameBase, count: int):
        self.vector_map[name] = count