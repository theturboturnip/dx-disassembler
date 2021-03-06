import ctypes
from pathlib import WindowsPath

from dx.dll_ex import WinDLLEx, LOAD_WITH_ALTERED_SEARCH_PATH
from dx.types import ID3D10Blob

dll_path = r"C:\Users\Samuel\PycharmProjects\DXBCDisassembler\dxc-artifacts\bin\d3dcompiler_dxc_bridge.dll"
original_dll_path = r"d3dcompiler_47.dll"
stable_dll_path = r"C:\Program Files (x86)\Windows Kits\10\Redist\D3D\x86\d3dcompiler_47.dll"
d3d11compiler_lib = WinDLLEx(original_dll_path)
d3d11decompiler_lib = d3d11compiler_lib

d3d11_compile_shader_proto = ctypes.WINFUNCTYPE(
    ctypes.HRESULT,

    ctypes.c_void_p,  # pSrcData
    ctypes.c_size_t,  # SrcDataSize
    ctypes.c_char_p,  # pSourceName
    ctypes.c_void_p,  # Macros (None is allowed)
    ctypes.c_void_p,  # D3D_COMPILE_STANDARD_FILE_INCLUDE = (ID3DInclude*)(UINT_PTR)1
    ctypes.c_char_p,  # pEntrypoint
    ctypes.c_char_p,  # pTarget
    ctypes.c_uint,  # Flags1
    ctypes.c_uint,  # Flags2
    ctypes.POINTER(ctypes.POINTER(ID3D10Blob)),  # shader data blob
    ctypes.POINTER(ctypes.POINTER(ID3D10Blob)),  # error data blob
)
d3d11_compile_shader = d3d11_compile_shader_proto(("D3DCompile", d3d11decompiler_lib))

d3d11_disassemble_shader_proto = ctypes.WINFUNCTYPE(
    ctypes.HRESULT,

    ctypes.c_void_p,  # pSrcData
    ctypes.c_size_t,  # SrcDataSize
    ctypes.c_uint,   # Flags
    ctypes.c_char_p,  # szComments

    ctypes.POINTER(ctypes.POINTER(ID3D10Blob)),  # disassembly blob
)
d3d11_disassemble_shader = d3d11_disassemble_shader_proto(("D3DDisassemble", d3d11compiler_lib))