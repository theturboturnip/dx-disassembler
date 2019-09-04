from itertools import chain

from dxbc.Errors import DXBCInstructionDecodeError
from dxbc.tokens import *
from dxbc.v2.program.Functions import TruncateToOutput, function_map, Function
from dxbc.v2.program.State import ProgramState
from dxbc.v2.program.Variables import *
from dxbc.v2.values.Scalar import cast_scalar
from dxbc.v2.values.Utils import get_type_string
from dxbc.v2.values.tokens import ValueToken, ValueHoldingToken
from utils import *
import copy


CT = CompoundToken
OT = OptionalToken

value_expr_token = ValueToken
arguments_token = OT(CT(
    value_expr_token,
    RepeatingToken(
        CT(RegexToken(",", "comma"), WhitespaceToken, value_expr_token)
    )
))
instruction_token = CT(WhitespaceToken, LineNumberToken, WhitespaceToken,
                       InstructionNameToken, OT(CT(WhitespaceToken, arguments_token, OT(NewlineToken))))


def extract_instruction_data(tokens: List[Token]):
    if not isinstance(tokens, list):
        tokens = list(tokens)
    instr_tokens = list(filter(lambda x: isinstance(x, InstructionNameToken), tokens))
    arg_tokens = list(filter(lambda x: isinstance(x, ValueHoldingToken), tokens))
    arg_vals = list(map(lambda x: x.value, arg_tokens))

    if len(instr_tokens) != 1:
        raise DXBCInstructionDecodeError("Expected 1 InstructionNameToken, got {}".format(len(instr_tokens)))

    return instr_tokens[0].str_data, arg_vals

def update_state(function: Function, input_vals: List[Value], output_value: Value,
                     current_state: ProgramState):
    global total_scalar_variables, total_vector_variables

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
        return (output_id.base_name.name in registers
                and (output_id not in output_deps[output_id] or
                     func_output_type is not current_state.get_type(output_id, function.output_type)))

    # Detect if we need to create any new variables
    # If a value is set based entirely on other components, all trace of the previous value is lost.
    # Therefore, it can be renamed to a new variable at this point.
    if any(output_needs_variable(output_id) for output_id in output_ids):
        output_scalar_type = func_output_type
        if len(output_ids) > 1:
            new_var_name = VarNameBase(f"vector_{total_vector_variables}")
            total_vector_variables += 1
            for (i, output_id) in enumerate(output_ids):
                current_state.set_scalar_map(
                    output_id,
                    SingleVectorComponent(new_var_name, VectorComponent(i), output_scalar_type, False),
                    output_scalar_type
                )
            current_state.set_vector_length(new_var_name, len(output_ids))
        else:
            new_var_name = VarNameBase(f"scalar_{total_scalar_variables}")
            total_scalar_variables += 1
            current_state.set_scalar_map(output_ids[0], ScalarVariable(new_var_name, output_scalar_type, False),
                              output_scalar_type)
        return True
    return False
    #print(f"{get_type_string(output_scalar_type, output_value.num_components)} {new_var_name};")

from shader_source import ps_instruction_str as instruction_str

remaining = instruction_str
# Any time an array access is made, all components are assumed to be of the mapped type
vector_constants = {
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
initial_state = {
    ScalarID(VarNameBase(name), comp): VariableState(None, t)
    for comp in VectorComponent
    for (name, t) in vector_constants.items()
}
initial_state.update({
    ScalarID(VarNameBase(name)): VariableState(None, t)
    for (name, t) in scalar_values.items()
})
initial_state.update({
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
current_state: ProgramState = ProgramState(initial_state, initial_vec_state)
state_stack = []
registers = [f"r{i}" for i in range(0, 7)]
#argument_truncations = {
#
#}

def infer_type(value: Value, state: ProgramState) -> Value:
    if value.scalar_type is not ScalarType.Untyped:
        return value

    if isinstance(value, ScalarValueBase):
        val_id = ScalarID(value)
        variable_type = state.get_type(val_id, default=None)
        if not variable_type:
            raise DXBCError(f"Variable for value {value} has no state, can't infer type")
        if variable_type == ScalarType.Untyped:
            # This type has been set to untyped, assume there's a reason and just pass it through
            # This is for things like Samplers and Textures which we don't care about for typing purposes
            return value
        new_type = variable_type
        return cast_scalar(value, new_type)
    else:#f isinstance(value, SwizzledVectorValue):
        return VectorValue([infer_type(c, state) for c in value.scalar_values], value.negated)


#def infer_type(value: Value, state: Dict[ScalarID, VariableState]):
#    return map_scalar_values(value, lambda x: infer_and_cast_to_scalar_type(x, state))


current_tick = 0
total_scalar_variables = 0
total_vector_variables = 0
while remaining:
    try:
        tokens, remaining = instruction_token.eat(remaining)
        # print(list_str(tokens))
    except DXBCError as e:
        current_instruction_line = remaining[:remaining.index("\n")]
        reraise(e, f"{{}} encountered when tokenizing {current_instruction_line}, tokenized {instruction_str[:-len(remaining)]}")
        break

    try:
        previous_state = current_state
        current_state = current_state.copy()
        instr_name, arg_vals = extract_instruction_data(tokens)
    except DXBCError as e:
        reraise(e, "{} encountered when disassembling " + list_str(tokens))
        break

    try:
        # Detect the function and do type-checking
        function = function_map[instr_name]

        if not function.output_type:
            input_vals = arg_vals
            output_value = None
        else:
            input_vals = arg_vals[1:]
            output_value = arg_vals[0]
            #output_value = map_scalar_values(lambda s: cast_scalar(s, function.output_type), output_value)

        # Validate input and infer types
        input_vals = [infer_type(x, current_state) for x in input_vals]
        function.validate_input_length(input_vals)

        # Apply argument truncation
        input_vals = function.truncate_args(input_vals, output_value)

        new_variable = False
        if output_value:
            new_variable = update_state(function, input_vals, output_value, current_state)

        def apply_remap(value: Value, state: ProgramState):
            if isinstance(value, SingleVectorComponent):
                name = copy.copy(state.get_name(ScalarID(value), value))
                name.negated = value.negated
                return name
            elif isinstance(value, SwizzledVectorValue):
                return VectorValue([state.get_name(ScalarID(comp), comp) for comp in value.scalar_values], value.negated)
            else:
                return value

        remapped_input = [apply_remap(x, previous_state) for x in input_vals]

        disassembly = ""
        if output_value:
            remapped_output = apply_remap(output_value, current_state)
            if new_variable:
                disassembly += f"{get_type_string(remapped_output.scalar_type, remapped_output.num_components)} "
            vec_length = current_state.get_vector_length(remapped_output)
            disassembly += f"{remapped_output.disassemble(vec_length)} = "

        disassembly += f"{function.disassemble_call(remapped_input, current_state)};"
        print (disassembly)

        #print(f"{apply_remap(output_value, current_state)} = {function.name} {list_str(remapped_input)}")
        #print(f"\tinput types: {list_str(x.scalar_type for x in input_vals)}")
        #print(f"\t{instr_name} {list_str(input_vals)} -> {output_value}")
        #print(f"\t{output_deps}")
    except DXBCError as e:
        reraise(e, f"{{}} encountered when executing {instr_name} {arg_vals}")
        break

    current_tick += 1

