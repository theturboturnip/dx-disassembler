from dxbc.v2.disassembly.Disassembler import Disassembler

from shader_source import ps_instruction_str as instruction_str

disassembler = Disassembler()
disassembler.disassemble_file(instruction_str)
#disassembler.disassemble_program_contents(instruction_str)
#print(disassembler.get_function_contents_hlsl(line_prefix="\t"))
print(disassembler.program.get_function_contents_hlsl())

# all the player character's thoughts