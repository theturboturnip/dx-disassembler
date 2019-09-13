import collections

from dxbc.v2.program.Action import Action
from dxbc.v2.program.State import ExecutionState, List
from dxbc.v2.values.Utils import get_type_string

class Program:
    initial_state: ExecutionState
    actions: List[Action]

    registers: List[str] = []

    def __init__(self, initial_state: ExecutionState, actions: List[Action]):
        self.initial_state = initial_state
        self.actions = actions

    def get_disassembled_shader(self) -> str:
        raise NotImplementedError()

    def get_function_contents_hlsl(self, line_prefix: str = ""):
        function_contents = ""
        for action in self.actions:
            line_disassembly = f"{line_prefix}"
            if action.remapped_out:
                if action.new_variable:
                    line_disassembly += f"{get_type_string(action.remapped_out.scalar_type, action.remapped_out.num_components)} "
                vec_length = action.new_state.get_vector_length(action.remapped_out)
                line_disassembly += f"{action.remapped_out.disassemble(vec_length)} = "

            line_disassembly += f"{action.func.disassemble_call(action.remapped_in, action.new_state)};\n"
            function_contents += line_disassembly
        return function_contents

    def get_declaration_hlsl(self, line_prefix: str = "") -> str:
        raise NotImplementedError()