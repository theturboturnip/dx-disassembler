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
    parser = argparse.ArgumentParser(description="Insert a pixel shader compiled from HLSL into a Yakuza .pso or .fxo file")
    parser.add_argument("hlsl_file", help="The file to extract from.", type=windows_path_arg)
    out_arg = parser.add_argument("-o", help="The file to output. If the filename is of the form \"ORIGINAL_FILE.(pso|fxo).hlsl\", defaults to \"ORIGINAL_FILE.(pso|fxo)\"")
    parser.add_argument("--no_backup", dest="backup", action="store_false")

    args = parser.parse_args()

    if not args.o:
        if (len(args.hlsl_file.suffixes) > 1 and
                args.hlsl_file.suffixes[0].lower() in [".pso", ".fxo"] and
                args.hlsl_file.suffix.lower() == ".hlsl"):
            args.o = args.hlsl_file.with_suffix("")
        else:
            raise argparse.ArgumentError(out_arg, "-o was not specified and hlsl_file was not in the correct format to autodetect the output.")
    output_path = WindowsPath(args.o)

    yk_file = import_yakuza_shader_file(args.o)
    backup_path: WindowsPath = args.o.with_suffix(args.o.suffix + ".original")
    if args.backup and not backup_path.exists():
        yk_file.write_to_path(backup_path)

    flags = ((1 << 11)  # D3DCOMPILE_ENABLE_STRICTNESS
             | (1 << 21)  # D3DCOMPILE_ALL_RESOURCES_BOUND
             | (1 << 15))  # D3DCOMPILE_OPTIMIZATION_LEVEL3

    with args.hlsl_file.open("r") as f:
        shader_src = f.read()

    shader_assembly = compile_shader(shader_src, str(args.hlsl_file), flags)

    yk_file.update_pixel_shader_data(shader_assembly)

    yk_file.write_to_path(args.o)

if __name__ == "__main__":
    sys.excepthook = show_exception_and_exit

    main()
