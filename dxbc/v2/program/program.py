from typing import Optional, Union, List

from dxbc.grammar.table_parser import Semantic
from dxbc.v2.definitions import VectorComponent
from dxbc.v2.program.semantics import SemanticSet
from dxbc.v2.types import ScalarType
from dxbc.v2.program.actions.action import Action
from dxbc.v2.program.declarations import DeclStorage, DeclName, Declaration
from dxbc.v2.program.state import ExecutionState
from dxbc.v2.program.variables import ScalarID
from dxbc.v2.values import *
from dxbc.v2.values.utils import get_type_string

specifiers = {
    "position": "SV_POSITION",
}

class Program:
    declarations: DeclStorage
    input_semantics: SemanticSet
    output_semantics: SemanticSet

    initial_state: ExecutionState
    actions: List[Action]

    registers: List[str] = []

    icb_contents: str

    def __init__(self, declarations: DeclStorage, initial_state: ExecutionState, actions: List[Action], input_semantics: SemanticSet, output_semantics: SemanticSet):
        self.declarations = declarations
        self.initial_state = initial_state
        self.actions = actions
        self.input_semantics = input_semantics
        self.output_semantics = output_semantics

    def get_disassembled_shader(self) -> str:
        return "\n".join([self.get_macros(), "", self.get_declaration_hlsl(), self.get_main_function_hlsl()])

    def get_main_function_hlsl(self, line_prefix: str = "", input_struct_name: str = "INPUT", output_struct_name: str = "OUTPUT"):
        start_mapping = self.get_start_mapping(
            self.declarations[DeclName.TypedPSInput] + self.declarations[DeclName.UntypedInput],
            self.declarations[DeclName.Output],
            line_prefix="\t")
        algo_hlsl = self.get_algorithm_hlsl(line_prefix="\t")
        end_mapping = self.get_end_mapping(
            self.declarations[DeclName.Output],
            line_prefix="\t")
        return \
f"""{output_struct_name} main({input_struct_name} input)
{{
    {start_mapping}

    {algo_hlsl}

    {end_mapping}
}}""".replace("\n", f"\n{line_prefix}")

    def get_start_mapping(self, input_decls: List[DeclName], output_decls: List[DeclName], line_prefix: str = ""):
        member_strs: List[str] = []

        for i in input_decls:
            member_val = i.value_list[0]
            member_name = member_val.get_var_name()

            type_str = get_type_string(self.initial_state.get_type_for_either_name(member_name),
                                       self.initial_state.get_vector_length(member_val, 1))
            member_strs.append(
                f"{type_str} {member_name} = input.{member_name};"
            )
        for i in output_decls:
            member_val = i.value_list[0]
            member_name = member_val.get_var_name()

            type_str = get_type_string(self.initial_state.get_type_for_either_name(member_name),
                                       self.initial_state.get_vector_length(member_val, 1))
            member_strs.append(
                f"{type_str} {member_name};"
            )

        full_member_str = f"\n{line_prefix}".join(member_strs)
        return full_member_str

    def get_end_mapping(self, output_decls: List[DeclName], line_prefix: str = ""):
        member_strs: List[str] = []
        for i in output_decls:
            member_val = i.value_list[0]
            member_name = member_val.get_var_name()

            type_str = get_type_string(self.initial_state.get_type_for_either_name(member_name),
                                       self.initial_state.get_vector_length(member_val, 1))
            member_strs.append(
                f"output.{member_name} = {member_name};"
            )

        full_member_str = f"\n".join(member_strs)
        return \
f"""OUTPUT output;
{full_member_str}
return output;""".replace("\n", f"\n{line_prefix}")

    def get_algorithm_hlsl(self, line_prefix: str = ""):
        function_contents = ""
        for action in self.actions:
            line_disassembly = f"\n{line_prefix}"
            if action.remapped_out:
                if action.new_variable:
                    line_disassembly += f"{get_type_string(action.remapped_out.scalar_type, action.remapped_out.num_components)} "
                vec_length = action.new_state.get_vector_length(action.remapped_out)
                line_disassembly += f"{action.remapped_out.disassemble(vec_length)} = "

            line_disassembly += f"{action.func.disassemble_call(action.remapped_in, action.new_state)};"
            function_contents += line_disassembly
        return function_contents

    def get_macros(self) -> str:
        return \
"""#define DISCARD_NZ(X) if (X != 0){ discard; };
inline uint BITRANGE_INSERT(uint width, uint offset, uint src, uint dest)
{
    uint mask = (0xffffffff >> (32 - width)) << offset;
    return ((src << offset) & mask) | (dest & ~mask);
}"""

    def create_struct_def(self, struct_name: str, decls: List[Declaration], semantics: SemanticSet, as_output: bool = False)-> str:
        decls = sorted(decls, key=lambda x: x.value_list[0].get_var_name().name)

        member_strs: List[str] = []
        for decl in decls:
            member_prefix = ""
            if len(decl.config_list):
                member_prefix = " ".join(c.scalar_name.name for c in decl.config_list) + " "
            #if len(decl.config_list) and isinstance(decl.config_list[0], ScalarVariable) and decl.config_list[0].scalar_name.name == "linearCentroid":
            #    member_prefix = "linear centroid "
            member_vec: Union[SwizzledVectorValue, SingleVectorComponent, ScalarVariable] = decl.value_list[0]
            member_name = member_vec.get_var_name()

            semantic = semantics.match_declaration(decl)
            output_decl = f": {semantic.semantic_name}"

            type_str = get_type_string(semantic.scalar_type,
                                       semantic.length)
            member_strs.append(
                f"{member_prefix}{type_str} {member_name}{output_decl};"
            )
        full_member_str = "\n\t".join(member_strs)

        return \
f"""struct {struct_name} {{
    {full_member_str}
}};"""

    def create_variable_decls(self, decls: List[Declaration], type_name: str):
        if len(decls) == 0:
            return ""
        value_names = ", ".join(decl.value_list[0].scalar_name.name for decl in decls)
        return f"{type_name} {value_names};"

    def create_constant_buffer_decl(self, decl: Declaration):
        cb_name = IndexedVarName(decl.value_list[0].scalar_name.name.lower(), decl.value_list[0].scalar_name.indices)
        type_str = get_type_string(self.initial_state.get_type_for_either_name(cb_name),
                                   self.initial_state.get_vector_length(cb_name, 4))
        register = int(cb_name.name.lower().replace("cb", ""))
        return \
f"""cbuffer {cb_name.name} : register(b{register})
{{
    {type_str} {cb_name};
}};"""

    def get_declaration_hlsl(self, line_prefix: str = "", input_struct_name: str = "INPUT", output_struct_name: str = "OUTPUT") -> str:
        input_struct = self.create_struct_def(
            input_struct_name, self.declarations[DeclName.TypedPSInput] + self.declarations[DeclName.UntypedInput], self.input_semantics)
        output_struct = self.create_struct_def(
            output_struct_name, self.declarations[DeclName.Output], self.output_semantics, True)

        texture_decls = self.create_variable_decls(self.declarations[DeclName.TextureToken], "Texture2D")
        sampler_decls = self.create_variable_decls(self.declarations[DeclName.SamplerToken], "SamplerState")

        icb_decl = f"float4x4 icb = {self.declarations.icb_buffers[0]};" if self.declarations.icb_buffers else ""

        cb_decls = [self.create_constant_buffer_decl(decl) for decl in self.declarations[DeclName.ConstantBufferToken]]

        return "\n".join([
            input_struct,
            output_struct,
            "",
            texture_decls,
            sampler_decls,
            "",
            icb_decl,
            "",
            *cb_decls,
            ""
        ]).replace("\n", f"\n{line_prefix}")
