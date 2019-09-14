import ctypes

from dx.dll import d3d11_disassemble_shader
from dx.types import ID3D10Blob, blob_to_bytes
from dx.errors import DXCallError


def decompile_shader(shader_data: bytes, flags: int = 0) -> str:
    disassembly_blob = ctypes.POINTER(ID3D10Blob)()

    flags = flags | 4  # Set ENABLE_INSTRUCTION_NUMBERING

    result = d3d11_disassemble_shader(
        shader_data, len(shader_data),
        flags,
        None, # No comments
        ctypes.byref(disassembly_blob)
    )
    if result:
        raise DXCallError(f"Disassembly failed with result {result}")

    disassembly_bytes = blob_to_bytes(disassembly_blob)
    return str(disassembly_bytes, 'utf-8')