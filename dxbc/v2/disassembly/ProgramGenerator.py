import collections
from copy import copy
from itertools import chain
from typing import Dict, List, Tuple, Sequence, Mapping, Optional

from dxbc.v2.Types import ScalarType
from dxbc.v2.disassembly.Tokenizer import NameToken, reraise
from dxbc.v2.program.Functions import Function, TruncateToOutput, function_map
from dxbc.v2.program.State import ProgramState, get_scalar_ids, DXBCError, SwizzledVectorValue, ScalarID, \
    VectorComponent, VariableState
from dxbc.v2.values import *
from dxbc.v2.values.Utils import get_type_string

Action = collections.namedtuple('Action', 'func remapped_in remapped_out new_variable new_state')

class ProgramGenerator:
    total_scalar_variables = 0
    total_vector_variables = 0

    instructions: List[Tuple[str, List[Value]]] = []
    registers: List[str] = []

    def __init__(self):
        pass

    def build_program(self, decl_data: Mapping[NameToken, List[List[Value]]],
                  instr_data: Sequence[Tuple[str, List[Value]]]) -> 'Program':
        initial_state, self.registers = self.generate_initial_state(decl_data)

        # for e in NameToken:
        #    print(f"{e.name}: {[x.tokens[3].str_data for x in declaration_dict[e]]}")

        current_tick: int = 0
        current_state: ProgramState = initial_state

        actions: List[Action] = []

        for (instr_name, arg_vals) in instr_data:

            previous_state = current_state
            current_state = current_state.copy()

            try:
                # Detect the function and do type-checking
                function = function_map[instr_name]

                if not function.output_type:
                    input_vals = arg_vals
                    output_value = None
                else:
                    input_vals = arg_vals[1:]
                    output_value = arg_vals[0]

                # Validate input and infer types
                input_vals = [current_state.infer_and_cast_type(x) for x in input_vals]
                function.validate_input_length(input_vals)

                # Apply argument truncation
                input_vals = function.truncate_args(input_vals, output_value)

                new_variable = False
                if output_value:
                    new_variable = self.update_state(function, input_vals, output_value, current_state)

                def apply_remap(value: Value, state: ProgramState):
                    if isinstance(value, SingleVectorComponent):
                        name = copy(state.get_name(ScalarID(value), value))
                        name.negated = value.negated
                        return name
                    elif isinstance(value, SwizzledVectorValue):
                        return VectorValue([state.get_name(ScalarID(comp), comp) for comp in value.scalar_values],
                                           value.negated)
                    else:
                        return value

                remapped_input = [apply_remap(x, previous_state) for x in input_vals]

                remapped_output = None
                if output_value:
                    remapped_output = apply_remap(output_value, current_state)

                actions.append(Action(func=function,
                                       remapped_in=remapped_input,
                                       remapped_out=remapped_output,
                                       new_variable=new_variable,
                                       new_state=current_state))

            except DXBCError as e:
                reraise(e, f"{{}} encountered when executing {instr_name} {arg_vals}")
                break

            current_tick += 1

        return Program(initial_state, actions)

    @staticmethod
    def generate_initial_state(decl_data: Mapping[NameToken, List[List[Value]]]) -> Tuple[ProgramState, List[str]]:
        initial_types: Dict[VarNameBase, ScalarType] = {}
        initial_vector_state: Dict[VarNameBase, int] = {}
        scalar_variable_names: List[VarNameBase] = []

        for x in decl_data[NameToken.ImmediateBufferToken]:
            # TODO: Assume immediate constant buffer is float4x4
            initial_types[VarNameBase("icb")] = ScalarType.Float
            initial_vector_state[VarNameBase("icb")] = 4
            break  # Only expect one

        for arg_tokens in decl_data[NameToken.ConstantBufferToken]:
            if (len(arg_tokens) == 0
                    or not isinstance(arg_tokens[0], ScalarVariable)
                    or not isinstance(arg_tokens[0].scalar_name, IndexedVarName)):
                raise DXBCError(
                    f"Expected constant buffer token to be of the form 'name[length]', got '{arg_tokens}'")
            base_name = arg_tokens[0].scalar_name.as_base()
            initial_types[base_name] = ScalarType.Float
            initial_vector_state[base_name] = 4

        for arg_tokens in (decl_data[NameToken.SamplerToken] + decl_data[NameToken.TextureToken]):
            if (len(arg_tokens) == 0
                    or not isinstance(arg_tokens[0], ScalarVariable)
                    or not type(arg_tokens[0].scalar_name) == VarNameBase):
                raise DXBCError(
                    f"Expected texture/sampler token to be of the form 'nameN', got '{arg_tokens}'")
            base_name = arg_tokens[0].scalar_name
            initial_types[base_name] = ScalarType.Untyped
            if "t" in base_name.name:
                initial_vector_state[base_name] = 4  # Textures are accessed as vectors in assembly
            else:
                scalar_variable_names.append(base_name)

        for arg_tokens in (decl_data[NameToken.TypedPSInput]
                           + decl_data[NameToken.UntypedInput]
                           + decl_data[NameToken.Output]):
            if len(arg_tokens) == 0:
                raise DXBCError(
                    f"Expected argument after input/output declaration, got '{arg_tokens}'")
            variable_value = arg_tokens[0]

            base_name: VarNameBase
            if isinstance(variable_value, ScalarVariable):
                base_name = variable_value.scalar_name
                component_count = 1
            elif isinstance(variable_value, SwizzledVectorValue):
                base_name = variable_value.vector_name
                component_count = max(variable_value.components) + 1
            elif isinstance(variable_value, SingleVectorComponent):
                base_name = variable_value.vector_name
                component_count = variable_value.component_name + 1
            else:
                raise DXBCError(
                    f"Expected input/output declaration to declare a ScalarVariable "
                    f", SwizzledVectorValue, or SingleVectorComponent, got {type(variable_value)}")

            if component_count == 3:
                component_count = 4  # Pad to pow2

            initial_types[base_name] = ScalarType.Uint if "Mask" in base_name.name else ScalarType.Float
            if base_name.name == "vCoverageMask":
                component_count = 4
            if component_count > 1:
                initial_vector_state[base_name] = component_count
            else:
                scalar_variable_names.append(base_name)

        initial_scalar_types: Dict[ScalarID, VariableState] = {
            ScalarID(name): VariableState(None, initial_types[name])
            for name in scalar_variable_names
        }
        initial_scalar_types.update({
            ScalarID(name, comp): VariableState(None, t)
            for (name, t) in initial_types.items() if name not in scalar_variable_names
            for comp in VectorComponent if comp < initial_vector_state[name]
        })
        initial_state = ProgramState(initial_scalar_types, initial_vector_state)

        registers = []
        for arg_tokens in decl_data[NameToken.RegisterCount]:
            if (len(arg_tokens) == 0
                    or not isinstance(arg_tokens[0], ImmediateScalar)):
                print(arg_tokens)
                raise DXBCError(
                    f"Expected register count to be an immediate, got '{arg_tokens}'")
            register_count = arg_tokens[0].value
            registers = [f"r{i}" for i in range(0, register_count)]
            break

        # if not registers:
        #    raise DXBCError("Expected RegisterCount declaration")

        return initial_state, registers

    def update_state(self, function: Function, input_vals: List[Value], output_value: Value,
                     current_state: ProgramState):

        output_ids = get_scalar_ids(output_value)

        # Determine data dependencies.
        output_deps = {x: None for x in output_ids}
        if isinstance(function, TruncateToOutput):
            # If we're truncating to output, each component of each input
            # maps directly to one component of the output.
            output_deps = {x: [] for x in output_ids}

            for input_val in input_vals:
                input_ids = get_scalar_ids(input_val)
                if len(input_ids) == 0:
                    # This means there weren't any named parts of this input
                    continue

                if len(input_ids) != len(output_ids):
                    raise DXBCError("Mismatch in input ids to output ids")

                for i in range(len(output_ids)):
                    output_deps[output_ids[i]].append(input_ids[i])

            # Remove dupes
            output_deps = {k: list(set(v)) for (k, v) in output_deps.items()}
        else:
            # Otherwise, every component of output depends on every component of input
            input_set = list(set(chain.from_iterable(get_scalar_ids(x) for x in input_vals)))
            output_deps = {k: input_set for k in output_deps}

        func_output_type = function.get_output_type(input_vals)

        def output_needs_variable(output_id):
            return (output_id.base_name.name in self.registers
                    and (output_id not in output_deps[output_id] or
                         func_output_type is not current_state.get_type(output_id, function.output_type)))

        # Detect if we need to create any new variables
        # If a value is set based entirely on other components, all trace of the previous value is lost.
        # Therefore, it can be renamed to a new variable at this point.
        if any(output_needs_variable(output_id) for output_id in output_ids):
            output_scalar_type = func_output_type
            if len(output_ids) > 1:
                new_var_name = VarNameBase(f"vector_{self.total_vector_variables}")
                self.total_vector_variables += 1
                current_state.set_vector_map(new_var_name, output_ids, output_scalar_type)
            else:
                new_var_name = VarNameBase(f"scalar_{self.total_scalar_variables}")
                self.total_scalar_variables += 1
                current_state.set_scalar_map(output_ids[0],
                                             ScalarVariable(new_var_name, output_scalar_type, False),
                                             output_scalar_type)
            return True
        return False

class Program:
    initial_state: ProgramState
    actions: List[Action]

    registers: List[str] = []

    def __init__(self, initial_state: ProgramState, actions: List[Action]):
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