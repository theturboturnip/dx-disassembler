from pathlib import WindowsPath

from dx.compile import compile_shader
from dxbc.grammar.parser import DisassemblyParser
from dxbc.v2.program.program import Program
from dxbc.v2.program.program_generator import ProgramGenerator
from yakuza.yk_shader_file import import_yakuza_shader_file, YkShaderFile
from dx.decompile import decompile_shader

def program_from_bytes(b: bytes) -> Program:
    shader_assembly = decompile_shader(b)
    dp = DisassemblyParser(shader_assembly)
    pg = ProgramGenerator()
    return pg.build_program(dp.declarations, dp.instructions, dp.input_semantics, dp.output_semantics)


def decompile_yakuza_shader(y: YkShaderFile):
    program = program_from_bytes(y.get_pixel_shader_data())

    print(program.get_disassembled_shader())

    flags = (1 << 11) | (1 << 21) | (1 << 15)
    compile_bytes = compile_shader(program.get_disassembled_shader(), "DISASSEMBLED_SHADER", flags)

    program2 = program_from_bytes(compile_bytes)
    print(program2.get_disassembled_shader())
    compile_bytes2 = compile_shader(program2.get_disassembled_shader(), "DISASSEMBLED_SHADER2", flags)


f = import_yakuza_shader_file(WindowsPath("./custom_data/sd_c1dzt[hair][vcol][ao].fxo"))
print(f)
decompile_yakuza_shader(f)

f2 = import_yakuza_shader_file(WindowsPath("./custom_data/ps_lighting_from_depth_ssss.pso"))
print(f2)

#print(decompile_shader(f2.get_pixel_shader_data()))
