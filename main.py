from dxbc.grammar.parser import DisassemblyParser
from dxbc.legacy.disassembly.Disassembler import Disassembler
from dxbc.v2.program.program_generator import ProgramGenerator

from shader_source import ps_instruction_str as instruction_str

dp = DisassemblyParser(instruction_str)
pg = ProgramGenerator()
print(pg.build_program(dp.declarations, []).initial_state.state_map.keys())


#disassembler = Disassembler()
#disassembler.disassemble_file(instruction_str)
##disassembler.disassemble_program_contents(instruction_str)
##print(disassembler.get_function_contents_hlsl(line_prefix="\t"))
#print(disassembler.program.get_function_contents_hlsl())

# all the player character's thoughts