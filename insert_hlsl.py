import argparse
import ctypes.util
import sys
from pathlib import WindowsPath

from dx.compile import compile_shader
from dx.decompile import decompile_shader
from dx.errors import DXCallError
from dxbc.grammar.parser import DisassemblyParser
from dxbc.v2.program.program_generator import ProgramGenerator
from utils import reraise
from yakuza.yk_shader_file import import_yakuza_shader_file


def show_exception_and_exit(exc_type, exc_value, tb):
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    input("Press key to exit.")
    sys.exit(-1)

def windows_path_arg(input: str):
    path = WindowsPath(input)
    if not path.exists():
        raise argparse.ArgumentTypeError(f"'{input}' is not an existing file!")
    return path

def main():
    parser = argparse.ArgumentParser(description="Extract the pixel shader HLSL from a Yakuza .pso or .fxo file")
    parser.add_argument("yakuza_file", help="The file to extract from.", type=windows_path_arg)
    parser.add_argument("-o", help="The file to output. Defaults to \"ORIGINAL_FILE.pxo.hlsl\"")
    parser.add_argument("-i", help="Ignore compilation errors for disassembled shader", action="store_true", dest="ignore")

    args = parser.parse_args()

    if not args.o:
        args.o = args.yakuza_file.with_suffix(args.yakuza_file.suffix + ".hlsl")
    output_path = WindowsPath(args.o)

    yk_file = import_yakuza_shader_file(args.yakuza_file)

    shader_assembly = decompile_shader(yk_file.get_pixel_shader_data())
    print(shader_assembly)
    dp = DisassemblyParser(shader_assembly)
    pg = ProgramGenerator()
    program = pg.build_program(dp.declarations, dp.instructions, dp.input_semantics, dp.output_semantics)

    try:
        flags = (1 << 11) | (1 << 21) | (1 << 15)
        compile_shader(program.get_disassembled_shader(), "DISASSEMBLED_SHADER", flags)
    except DXCallError as e:
        if not args.ignore:
            reraise(e, "Got error when compiling disassembled shader, use -i to ignore." + "\n{}")

    with output_path.open("w") as f:
        f.write(program.get_disassembled_shader())

if __name__ == "__main__":
    sys.excepthook = show_exception_and_exit

    main()
