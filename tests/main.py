from dx.compile import compile_shader
from dx.decompile import decompile_shader
from dxbc.grammar.parser import DisassemblyParser
from dxbc.v2.program.program_generator import ProgramGenerator

from shader_source import ps_instruction_str as instruction_str

dp = DisassemblyParser(instruction_str)
pg = ProgramGenerator()
program = pg.build_program(dp.declarations, dp.instructions, dp.input_semantics, dp.output_semantics)
#print(dp.declarations[DeclName.TypedPSInput])
#print(dp.declarations[DeclName.UntypedInput])
#print(program.get_disassembled_shader())

flags = (1 << 11) | (1 << 21) | (1 << 15)
compile_bytes = compile_shader(program.get_disassembled_shader(), "DISASSEMBLED_SHADER", flags)
print(compile_bytes)
print(decompile_shader(compile_bytes, 0))

#disassembler = Disassembler()
#disassembler.disassemble_file(instruction_str)
##disassembler.disassemble_program_contents(instruction_str)
##print(disassembler.get_function_contents_hlsl(line_prefix="\t"))
#print(disassembler.program.get_function_contents_hlsl())

# all the player character's thoughts