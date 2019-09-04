from abc import ABC
from enum import Enum
from typing import Union, List, Optional, Type, Tuple, Dict

from dxbc.Errors import DXBCError
from dxbc.v2.Types import VectorType, ScalarType, get_least_permissive_container_type
from dxbc.v2.program import State
from dxbc.v2.program.State import ProgramState
from dxbc.v2.values import ScalarValueBase, Value, VectorValueBase, mask_components, trim_components, \
    SwizzledVectorValue
from dxbc.v2.values.Scalar import cast_scalar, reinterpret_scalar, SingleVectorComponent
from dxbc.v2.values.Utils import map_scalar_values, get_type_string

GenericValue = Value
GenericValueType = Union[ScalarType, VectorType]

class TypeHole:
    pass

ArgumentType = Union[ScalarType, TypeHole]


class ArgumentTruncation:
    def truncate_args(self, input_args: List[GenericValue], output_arg: GenericValue):
        """
        Creates a copy of input_args, truncates the values as it desires,
        and ends.
        """
        raise NotImplementedError()

class NonNullArgumentTruncation(ArgumentTruncation, ABC):
    """
    Inherited from by all implemented argument truncations.
    """
    pass

class NullTruncate(NonNullArgumentTruncation):
    def truncate_args(self, input_args, output_arg):
        return input_args

class TruncateToOutput(NonNullArgumentTruncation):
    def truncate_args(self, input_args, output_arg):
        output_mask = output_arg.get_output_mask()
        return [mask_components(arg, output_mask) for arg in input_args]

class TruncateToLength(NonNullArgumentTruncation, ABC):
    pass

def makeTruncateToLength(length: int):
    class TruncateToLength_Impl(TruncateToLength):
        def truncate_args(self, input_args, output_arg):
            return [trim_components(arg, length) for arg in input_args]
    return TruncateToLength_Impl

class TextureArgumentTruncation(NonNullArgumentTruncation):
    def truncate_args(self, input_args: List[GenericValue], output_arg: GenericValue):
        return [
            trim_components(input_args[0], 2),
            trim_components(input_args[1], 1),
            trim_components(input_args[2], 1),
        ]

class Function(ArgumentTruncation):
    name: str
    input_types: List[ArgumentType]
    output_type: Optional[ArgumentType]

    def __init__(self, name, input_types, output_type):
        if not isinstance(self, NonNullArgumentTruncation):
            raise DXBCError("Function must have some form of argument truncation")
        self.name = name
        self.input_types = input_types
        self.output_type = output_type

    def validate_input_length(self, input_args: List[Value]):
        if len(self.input_types) != len(input_args):
            raise DXBCError(f"Mismatched argument lengths for {self.name}: "
                            f"expected {len(self.input_types)}, got {len(input_args)}")

    def disassemble_call(self, input_args: List[Value], current_state: ProgramState):
        if len(input_args) == 0:
            return self.name
        casted_input_args = self.get_input_strings(input_args, self.determine_typehole_type(input_args), current_state)
        return "{}({})".format(self.name, ", ".join(casted_input_args))

    def get_output_type(self, input_args):
        if type(self.output_type) is TypeHole:
            return self.determine_typehole_type(input_args)
        return self.output_type

    def get_input_strings(self, input_args: List[Value], typehole_value: Optional[ScalarType], current_state: ProgramState) -> List[str]:
        casted_input_args = [""] * len(input_args)
        for (i, t) in enumerate(self.input_types):
            t = t if type(t) is not TypeHole else typehole_value
            arg = input_args[i]
            vector_type_length = current_state.get_vector_length(arg)
            if not t.encapsulates(arg.scalar_type):
                casted_input_args[i] = (
                        f"{str(get_type_string(t, arg.num_components))}" +
                        f"({arg.disassemble(vector_type_length)})"
                )
            elif t == ScalarType.Untyped and isinstance(arg, (SwizzledVectorValue, SingleVectorComponent)):
                casted_input_args[i] = f"{arg.vector_name}"
            else:
                casted_input_args[i] = f"{arg.disassemble(vector_type_length)}"
        return casted_input_args

    def determine_typehole_type(self, input_args) -> Optional[ScalarType]:
        typehole_types = [input_args[i].scalar_type for (i,t) in enumerate(self.input_types) if type(t) is TypeHole]
        if len(typehole_types) == 0:
            return None
        return get_least_permissive_container_type(*typehole_types)

class InfixFunction(Function):
    def disassemble_call(self, input_args: List[Value], current_state: ProgramState):
        casted_input_args = self.get_input_strings(input_args, self.determine_typehole_type(input_args), current_state)
        return f" {self.name} ".join(casted_input_args)

class MoveFunction(Function):
    def disassemble_call(self, input_args: List[Value], current_state: ProgramState):
        casted_input_args = self.get_input_strings(input_args, self.determine_typehole_type(input_args), current_state)
        return casted_input_args[0]

class MulAddFunction(Function):
    def disassemble_call(self, input_args: List[Value], current_state: ProgramState):
        casted_input_args = self.get_input_strings(input_args, self.determine_typehole_type(input_args), current_state)
        return "({} * {}) + {}".format(casted_input_args[0], casted_input_args[1], casted_input_args[2])

class MoveCondFunction(Function):
    def disassemble_call(self, input_args: List[Value], current_state: ProgramState):
        casted_input_args = self.get_input_strings(input_args, self.determine_typehole_type(input_args), current_state)
        return "{} ? {} : {}".format(casted_input_args[0], casted_input_args[1], casted_input_args[2])

#class BitfieldInsertFunction(Function):
#    def disassemble_call(self, input_args: List[Value]):
#        casted_input_args = self.get_input_strings(input_args, self.determine_typehole_type(input_args))
#        return "{{ uint mask = (0xffffffff >> (32 - {0})) << {1}; {2} = (({3} << {1}) & mask) | ({4} & ~mask); }}".format(casted_input_args[0], casted_input_args[1], casted_input_args[2])

def make_function(base_func_type: Type[Function], base_trunc_type: Type[ArgumentTruncation],
                  name: str, input_types: List[ArgumentType], output_type: Optional[ArgumentType] = None) -> Function:
    func_type = type(f"Function_{name}", (base_func_type, base_trunc_type), {
        "__init__": lambda self: (
            base_func_type.__init__(self, name, input_types, output_type)
        )
    })
    return func_type()

def make_arithmetic_function(name: str, scalar_type: ScalarType) -> Function:
    return make_function(InfixFunction, TruncateToOutput, name, [scalar_type, scalar_type], scalar_type)

def make_boolean_comparison(name: str, scalar_type: ScalarType) -> Function:
    return make_function(InfixFunction, TruncateToOutput, name, [scalar_type, scalar_type], ScalarType.Uint)

def make_logical_operation(name: str) -> Function:
    return make_function(InfixFunction, TruncateToOutput, name, [ScalarType.Uint, ScalarType.Uint], ScalarType.Uint)

def get_closest_types(value: Value) -> GenericValueType:
    if isinstance(value, ScalarValueBase):
        return value.scalar_type
    elif isinstance(value, VectorValueBase):
        return VectorType(value.scalar_type, value.num_components)


function_map: Dict[str, Function] = {
    "sample_indexable(texture2d)(float,float,float,float)":
        make_function(
            Function,
            TextureArgumentTruncation,
            "sample_texture",
            [
                ScalarType.Float,   # UV
                ScalarType.Untyped, # Texture
                ScalarType.Untyped  # Sampler
            ],
            ScalarType.Float
        ),

    "discard_nz" : make_function(Function, NullTruncate, "discard_nz", [ScalarType.Untyped], None),

    "add": make_arithmetic_function("+", ScalarType.Float),
    "iadd": make_arithmetic_function("+", ScalarType.Uint),
    "mul": make_arithmetic_function("*", ScalarType.Float),
    "div": make_arithmetic_function("/", ScalarType.Float),

    "mad": make_function(MulAddFunction, TruncateToOutput, "mul_add",
                         [ScalarType.Float] * 3,
                         ScalarType.Float),

    "lt" : make_boolean_comparison("<", ScalarType.Float),
    "eq": make_boolean_comparison("==", ScalarType.Float),
    "ne": make_boolean_comparison("!=", ScalarType.Float),
    "ieq": make_boolean_comparison("==", ScalarType.Uint),
    "ine": make_boolean_comparison("!=", ScalarType.Uint),

    "or": make_logical_operation("|"),
    "and": make_logical_operation("&"),
    "xor": make_logical_operation("^"),

    "ishl": make_arithmetic_function("<<", ScalarType.Uint),
    "bfi": make_function(
        Function,
        TruncateToOutput,
        "bitrange_insert",
        [ScalarType.Uint] * 4,
        ScalarType.Uint
    ),

    "mov": make_function(
        MoveFunction,
        TruncateToOutput,
        "move",
        [TypeHole()],
        TypeHole()
    ),
    "movc": make_function(
        MoveCondFunction,
        TruncateToOutput,
        "move_conditional",
        [ScalarType.Uint, TypeHole(), TypeHole()],
        TypeHole()
    ),

    "min": make_function(
        Function, TruncateToOutput,
        "min",
        [TypeHole()] * 2,
        TypeHole()),
    "max": make_function(
        Function, TruncateToOutput,
        "max",
        [TypeHole()] * 2,
        TypeHole()),
    "sqrt": make_function(Function, TruncateToOutput, "sqrt", [ScalarType.Float], ScalarType.Float),
    "rsq": make_function(Function, TruncateToOutput, "1.0 / sqrt", [ScalarType.Float], ScalarType.Float),
    "f16tof32": make_function(Function, TruncateToOutput, "f16tof32", [ScalarType.Uint], ScalarType.Float),
    "ftou": make_function(MoveFunction, TruncateToOutput, "cast_float_to_uint_NAME_UNUSED", [ScalarType.Uint], ScalarType.Uint),
    "dp2": make_function(Function, makeTruncateToLength(2), "dot", [ScalarType.Float, ScalarType.Float], ScalarType.Float),
    "dp3": make_function(Function, makeTruncateToLength(3), "dot", [ScalarType.Float, ScalarType.Float], ScalarType.Float),

    "ret": make_function(Function, NullTruncate, "return", [], None)
}