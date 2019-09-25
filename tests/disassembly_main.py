from dx.compile import compile_shader
from dx.decompile import decompile_shader
from dxbc.grammar.parser import DisassemblyParser
from dxbc.v2.program.program_generator import ProgramGenerator

path = "./tests/custom_shader.pso"

with open(path, "rb") as f:
    shader_bytes = f.read()

shader_assembly = decompile_shader(shader_bytes)
print(shader_assembly)
dp = DisassemblyParser(shader_assembly)
#print(dp.input_semantics)
pg = ProgramGenerator()
program = pg.build_program(dp.declarations, dp.instructions, dp.input_semantics, dp.output_semantics)

print(program.get_disassembled_shader())

flags = (1 << 11) | (1 << 21) | (1 << 15)
compile_bytes = compile_shader(program.get_disassembled_shader(), "DISASSEMBLED_SHADER", flags)
