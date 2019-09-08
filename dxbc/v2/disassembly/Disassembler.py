import collections
from itertools import chain

from dxbc.v2.program.Functions import *
from dxbc.v2.program.State import ProgramState
from dxbc.v2.disassembly.Tokenizer import Tokenizer, INSTRUCTION_TOKEN, NewlineToken, WhitespaceToken, \
    SHADER_START_TOKEN, DECLARATION_TOKEN, NameToken
from dxbc.v2.program.Variables import *
from dxbc.v2.values.Utils import get_type_string
from dxbc.v2.values.tokens import ValueToken
from utils import *

# Any time an array access is made, all components are assumed to be of the mapped type
"""vector_constants = {
    "cb5": ScalarType.Float,
    "cb6": ScalarType.Float,
    "cb7": ScalarType.Float,
    "cb12": ScalarType.Float,
    "cb13": ScalarType.Float,

    "icb": ScalarType.Float,

    "v0": ScalarType.Float,
    "v1": ScalarType.Float,
    "v2": ScalarType.Float,
    "v3": ScalarType.Float,
    "v4": ScalarType.Float,
    "vCoverageMask": ScalarType.Uint,
    "values": ScalarType.Float,

    "t0": ScalarType.Untyped,
    "t1": ScalarType.Untyped,
    "t2": ScalarType.Untyped,

    "o0": ScalarType.Float,
    "o1": ScalarType.Float,
    "o2": ScalarType.Float,
    "o3": ScalarType.Float,
}
scalar_values = {
    "oMask": ScalarType.Uint
}
initial_scalar_types = {
    ScalarID(VarNameBase(name), comp): VariableState(None, t)
    for comp in VectorComponent
    for (name, t) in vector_constants.items()
}
initial_scalar_types.update({
    ScalarID(VarNameBase(name)): VariableState(None, t)
    for (name, t) in scalar_values.items()
})
initial_scalar_types.update({
    ScalarID(VarNameBase(name)): VariableState(None, ScalarType.Untyped)
    for name in [
        "s0", "s1", "s2",
    ]
})
initial_vec_state = {
    VarNameBase(name): 4
    for name, scalar_type in vector_constants.items()
    if scalar_type == ScalarType.Float
}
registers = [f"r{i}" for i in range(0, 7)]"""

Action = collections.namedtuple('Action', 'func remapped_in remapped_out new_variable new_state')


class Disassembler:
    total_scalar_variables = 0
    total_vector_variables = 0

    initial_state: Optional[ProgramState]
    instructions: List[Tuple[str, List[Value]]]
    actions: List[Action] = []

    registers: List[str] = []


    def __init__(self):
        self.tokenizer = Tokenizer()
        self.instructions = []
        self.initial_state = None # ProgramState(initial_scalar_types, initial_vec_state)

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

    def disassemble_file(self, file_contents: str):
        tokens, remaining = self.tokenizer.tokenize_file(file_contents)
        tokens = [x for x in tokens if not isinstance(x, (WhitespaceToken, NewlineToken))]
        if len(tokens) == 0 or not isinstance(tokens[0], SHADER_START_TOKEN):
            raise DXBCError("Expected SHADER_START_TOKEN at the beginning of the file")

        declaration_tokens = [x for x in tokens if isinstance(x, DECLARATION_TOKEN)]
        declaration_pairs = [(NameToken.from_type(type(x.tokens[1])), x) for x in declaration_tokens]
        declaration_dict = {e: [x for x_e, x in declaration_pairs if x_e == e] for e in NameToken}

        initial_types: Dict[VarNameBase, ScalarType] = {}
        initial_vector_state: Dict[VarNameBase, int] = {}
        scalar_variable_names: List[VarNameBase] = []

        for x in declaration_dict[NameToken.ImmediateBufferToken]:
            # TODO: Assume immediate constant buffer is float4x4
            initial_types[VarNameBase("icb")] = ScalarType.Float
            initial_vector_state[VarNameBase("icb")] = 4
            break # Only expect one
        for x in declaration_dict[NameToken.ConstantBufferToken]:
            arg_tokens = [t for t in x.tokens[3].tokens if hasattr(t, "value")]
            if (len(arg_tokens) == 0
                    or not isinstance(arg_tokens[0].value, ScalarVariable)
                    or not isinstance(arg_tokens[0].value.scalar_name, IndexedVarName)):
                print(x.tokens[3].tokens)
                raise DXBCError(
                    f"Expected constant buffer token to be of the form 'name[length]', got '{x.tokens[3].str_data}'")
            base_name = arg_tokens[0].value.scalar_name.as_base()
            initial_types[base_name] = ScalarType.Float
            initial_vector_state[base_name] = 4
        for x in (declaration_dict[NameToken.SamplerToken] + declaration_dict[NameToken.TextureToken]):
            arg_tokens = [t for t in x.tokens[3].tokens if hasattr(t, "value")]
            if (len(arg_tokens) == 0
                    or not isinstance(arg_tokens[0].value, ScalarVariable)
                    or not type(arg_tokens[0].value.scalar_name) == VarNameBase):
                raise DXBCError(
                    f"Expected texture/sampler token to be of the form 'nameN', got '{x.tokens[3].str_data}'")
            base_name = arg_tokens[0].value.scalar_name
            initial_types[base_name] = ScalarType.Untyped
            if "t" in base_name.name:
                initial_vector_state[base_name] = 4 # Textures are accessed as vectors in assembly
            else:
                scalar_variable_names.append(base_name)
        for x in (declaration_dict[NameToken.TypedPSInput]
                  + declaration_dict[NameToken.UntypedInput]
                  + declaration_dict[NameToken.Output]):
            arg_tokens = [t for t in x.tokens[3].tokens if hasattr(t, "value")]
            if len(arg_tokens) == 0:
                raise DXBCError(
                    f"Expected argument after input/output declaration, got '{x.tokens[3].str_data}'")

            base_name: VarNameBase
            if isinstance(arg_tokens[0].value, ScalarVariable):
                base_name = arg_tokens[0].value.scalar_name
                component_count = 1
            elif isinstance(arg_tokens[0].value, SwizzledVectorValue):
                base_name = arg_tokens[0].value.vector_name
                component_count = max(arg_tokens[0].value.components) + 1
            elif isinstance(arg_tokens[0].value, SingleVectorComponent):
                base_name = arg_tokens[0].value.vector_name
                component_count = arg_tokens[0].value.component_name + 1
            else:
                raise DXBCError(
                    f"Expected input/output declaration to declare a ScalarVariable "
                    f", SwizzledVectorValue, or SingleVectorComponent, got {type(arg_tokens[0].value)}")

            if component_count == 3:
                component_count = 4 # Pad to pow2

            initial_types[base_name] = ScalarType.Uint if "Mask" in base_name.name else ScalarType.Float
            if component_count > 1:
                initial_vector_state[base_name] = component_count
            else:
                scalar_variable_names.append(base_name)

        #print(scalar_variable_names)
        #print(initial_vector_state)

        for x in declaration_dict[NameToken.RegisterCount]:
            arg_tokens = [t for t in x.tokens[3].tokens if hasattr(t, "value")]
            if (len(arg_tokens) == 0
                    or not isinstance(arg_tokens[0].value, ImmediateScalar)):
                print(arg_tokens)
                raise DXBCError(
                    f"Expected register count to be an immediate, got '{x.tokens[3].str_data}'")
            register_count = arg_tokens[0].value.value
            self.registers = [f"r{i}" for i in range(0, register_count)]
            break

        #if not self.registers:
        #    raise DXBCError("Expected RegisterCount declaration")

        initial_scalar_types: Dict[ScalarID, VariableState] = {
            ScalarID(name): VariableState(None, initial_types[name])
            for name in scalar_variable_names
        }
        #print(initial_scalar_types)
        initial_scalar_types.update({
            ScalarID(name, comp): VariableState(None, t)
            for (name, t) in initial_types.items() if name not in scalar_variable_names
            for comp in VectorComponent if comp < initial_vector_state[name]
        })

        self.initial_state = ProgramState(initial_scalar_types, initial_vector_state)

        for e in NameToken:
            print(f"{e.name}: {[x.tokens[3].str_data for x in declaration_dict[e]]}")

        current_tick: int = 0
        current_state: ProgramState = self.initial_state

        for instr_tokens in [x.tokens for x in tokens if isinstance(x, INSTRUCTION_TOKEN)]:
            (instr_name, arg_vals) = self.tokenizer.extract_instruction_data(instr_tokens)

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

                self.actions.append(Action(func=function,
                                           remapped_in=remapped_input,
                                           remapped_out=remapped_output,
                                           new_variable=new_variable,
                                           new_state=current_state))

            except DXBCError as e:
                reraise(e, f"{{}} encountered when executing {instr_name} {arg_vals}")
                break

            current_tick += 1

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

