from dxbc.v2.disassembly.Disassembler import Disassembler

from shader_source import ps_instruction_str as instruction_str

disassembler = Disassembler()
disassembler.disassemble_program_contents(instruction_str)
