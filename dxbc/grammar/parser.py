from collections import Mapping
from typing import List, Dict, Union, Tuple

from antlr4 import *

from dxbc.Errors import DXBCError
from dxbc.v2.definitions import VectorComponent
from dxbc.v2.types import ScalarType
from dxbc.v2.program.decl_name import DeclName, DeclStorage, Declaration
from dxbc.v2.values import *
from dxbc.v2.values.brace_list import BraceList
from .antlr_files.DXBCListener import DXBCListener
from .antlr_files.DXBCLexer import DXBCLexer
from .antlr_files.DXBCParser import DXBCParser

decl_name_str_map = {
    "dcl_globalFlags": DeclName.GlobalFlags,
    "dcl_immediateConstantBuffer": DeclName.ImmediateBufferToken,
    "dcl_constantbuffer": DeclName.ConstantBufferToken,
    "dcl_sampler": DeclName.SamplerToken,
    "dcl_resource_texture2d": DeclName.TextureToken,
    "dcl_input_ps": DeclName.TypedPSInput,

    "dcl_input": DeclName.UntypedInput,
    "dcl_input_ps_siv": DeclName.UntypedInput,

    "dcl_output": DeclName.Output,
    "dcl_temps": DeclName.RegisterCount
}


def parse_var_name(variable_name_ctx: DXBCParser.Variable_nameContext) -> VarNameBase:
    if variable_name_ctx.array_index():
        array_idx_ctx: DXBCParser.Array_indexContext = variable_name_ctx.array_index()
        values = [parse_component_value(x) for x in array_idx_ctx.component_value()]
        return IndexedVarName(str(variable_name_ctx.ID()), values)
    return VarNameBase(str(variable_name_ctx.ID()))

def parse_component_value(scalar_ctx: DXBCParser.Component_valueContext) -> ScalarValueBase:
    negated = scalar_ctx.SUB_OP() is not None
    scalar_ctx = scalar_ctx.scalar_value()

    return parse_scalar(scalar_ctx, negated)

def parse_scalar(scalar_ctx: Union[DXBCParser.Scalar_valueContext], negated:bool) -> ScalarValueBase:
    if scalar_ctx.immediate_scalar():
        immediate_ctx: DXBCParser.Immediate_scalarContext = scalar_ctx.immediate_scalar()
        if immediate_ctx.HEX_IMMEDIATE_SCALAR():
            value = int(str(immediate_ctx.HEX_IMMEDIATE_SCALAR()), 16)
            scalar_type = ScalarType.Hex
        elif immediate_ctx.INT_IMMEDIATE_SCALAR():
            value = int(str(immediate_ctx.INT_IMMEDIATE_SCALAR()))
            scalar_type = ScalarType.Uint
        elif immediate_ctx.FLOAT_IMMEDIATE_SCALAR():
            value = float(str(immediate_ctx.FLOAT_IMMEDIATE_SCALAR()))
            scalar_type = ScalarType.Float
        else:
            raise DXBCError("None of immediate_scalar values were present")
        return ImmediateScalar(value, scalar_type, negated)
    elif scalar_ctx.scalar_variable():
        return ScalarVariable(
            parse_var_name(scalar_ctx.scalar_variable().variable_name()),
            ScalarType.Untyped,
            negated
        )
    elif scalar_ctx.single_vector_component():
        return SingleVectorComponent(
            parse_var_name(scalar_ctx.single_vector_component().variable_name()),
            VectorComponent[str(scalar_ctx.single_vector_component().single_component().COMPONENT())],
            ScalarType.Untyped,
            negated
        )
    raise DXBCError(f"Unknown scalar_ctx type: {type(scalar_ctx)}")

def parse_vector(vector_ctx: DXBCParser.Vector_valueContext, negated:bool) -> Value:
    scalar_components = []
    if vector_ctx.swizzled_vector_variable():
        vector_components = str(vector_ctx.swizzled_vector_variable().swizzle_components().COMPONENT_STR())
        base_name = parse_var_name(vector_ctx.swizzled_vector_variable().variable_name())
        scalar_components = [
            SingleVectorComponent(
                base_name,
                VectorComponent[vector_component],
                ScalarType.Untyped,
                False
            )
            for vector_component in vector_components
        ]
    elif vector_ctx.immediate_vector():
        scalar_components = [parse_component_value(component_value) for component_value in vector_ctx.immediate_vector().component_value()]
        if len(scalar_components) == 1:
            return scalar_components[0]

    return VectorValue(scalar_components, negated)

def parse_brace_list(value_ctx: DXBCParser.Brace_list_or_valContext) -> BraceList:
    if not value_ctx.brace_list():
        raise DXBCError(f"Expected brace_list, got {type(value_ctx)}")
    return BraceList(value_ctx.brace_list().getText())

def parse_value(value_ctx: Union[DXBCParser.Brace_list_or_valContext, DXBCParser.ValueContext]) -> Value:
    if isinstance(value_ctx, DXBCParser.Brace_list_or_valContext):
        if value_ctx.brace_list():
            raise DXBCError(f"Expected ValueContext, got brace list")
        value_ctx = value_ctx.value()

    negated = value_ctx.SUB_OP() is not None

    if value_ctx.scalar_value():
        value = parse_scalar(value_ctx.scalar_value(), negated)
    elif value_ctx.vector_value():
        value = parse_vector(value_ctx.vector_value(), negated)
    else:
        raise DXBCError("ValueContext wasn't a vector or scalar")

    return value

class DisassemblyParser(DXBCListener):
    declarations: DeclStorage
    instructions: List[Tuple[str, List[Value]]]

    def __init__(self, str_data: str):
        input_stream = InputStream(str_data)
        lexer = DXBCLexer(input_stream)
        stream = CommonTokenStream(lexer)
        parser = DXBCParser(stream)
        tree = parser.dxbc_file()

        self.declarations = DeclStorage()
        self.instructions = []

        walker = ParseTreeWalker()
        walker.walk(self, tree)

        #print(self.declarations)

    def enterConfigured_declaration(self, ctx:DXBCParser.Configured_declarationContext):
        decl_name = decl_name_str_map[str(ctx.DECL_NAME())]
        #print(f"\nconfigured decl name: {DeclName(decl_name).name}")

        config = parse_value(ctx.brace_list_or_val())
        value_list = [parse_value(value_ctx) for value_ctx in ctx.value()]
        self.declarations[decl_name].append(Declaration(config, value_list))

    def enterSimple_declaration(self, ctx:DXBCParser.Simple_declarationContext):
        decl_name = decl_name_str_map[str(ctx.DECL_NAME())]
        #print(f"\nsimple decl name: {DeclName(decl_name).name}")

        if decl_name is DeclName.ImmediateBufferToken:
            self.declarations.icb_buffers.append(parse_brace_list(ctx.brace_list_or_val()))
        else:
            value_list = [parse_value(ctx.brace_list_or_val())] + [parse_value(value_ctx) for value_ctx in ctx.value()]
            self.declarations[decl_name].append(Declaration(None, value_list))

    def enterInstruction(self, ctx: DXBCParser.InstructionContext):
        instr_idx = int(ctx.INT_IMMEDIATE_SCALAR().getText())
        if len(self.instructions) != instr_idx:
            raise DXBCError(f"Expected instruction #{len(self.instructions)}, got #{instr_idx}")
        instr_name = str(ctx.instruction_name().getText())
        #print(f"\ninstr name: {instr_name}")
        value_list = [parse_value(value_ctx) for value_ctx in ctx.value()]
        #print(f"values: {value_list}")
        self.instructions.append((instr_name, value_list))

