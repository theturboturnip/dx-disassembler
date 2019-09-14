import ctypes

from dx.errors import DXCallError
from dx.types import *

d3d11compiler_lib = ctypes.WinDLL("d3dcompiler_47.dll")

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
d3d11_compile_shader = d3d11_compile_shader_proto(("D3DCompile", d3d11compiler_lib))

def blob_to_bytes(blob: ctypes.POINTER(ID3D10Blob)) -> bytes:
    print(blob.contents)
    print(blob.contents.vtable.contents)
    blob_ptr = ctypes.cast(blob.contents.vtable.contents.GetBufferPointer(blob), ctypes.POINTER(ctypes.c_byte))
    blob_size = blob.contents.vtable.contents.GetBufferSize(blob)
    print(type(blob_size))
    print(blob_ptr)
    bytes_array = (ctypes.c_byte * blob_size).from_address(ctypes.cast(blob_ptr, ctypes.c_void_p).value)
    return bytes(bytes_array)

def compile_shader(src_shader: str, file_name: str, flags: int = 0, entry_point: str = "main", compile_target: str = "ps_5_0") -> bytes:
    b_src_shader = src_shader.encode("utf-8")
    b_file_name = file_name.encode("utf-8")
    b_entry_point = entry_point.encode("utf-8")
    b_compile_target = compile_target.encode("utf-8")

    blob_ptr_type = ctypes.POINTER(ID3D10Blob)
    shader_data_blob = blob_ptr_type()
    error_data_blob = blob_ptr_type()

    print(type(shader_data_blob))
    print(type(ctypes.byref(shader_data_blob)))
    print(d3d11_compile_shader.argtypes)

    result = 0
    try:
        result = d3d11_compile_shader(
            b_src_shader, len(b_src_shader), # Compile source data
            b_file_name,                   # as file_name
            None,                        # with no macros
            1,                           # with the default include handler
            b_entry_point,                 # starting at the specified entry point
            b_compile_target,              # with this shader model

            flags,
            0,

            # Output into our shader data blob and error blob pointers
            ctypes.byref(shader_data_blob), ctypes.byref(error_data_blob)
        )
    except WindowsError as we:
        print(we.args[0])
        raise we
    finally:
        if result or error_data_blob:
            error_bytes = blob_to_bytes(error_data_blob)
            error_str = str(error_bytes, "utf-8")
            error_data_blob.contents.vtable.contents.Release(error_data_blob)
            raise DXCallError(error_str)
    shader_data_bytes = blob_to_bytes(shader_data_blob)
    shader_data_blob.contents.vtable.contents.Release(shader_data_blob)
    return shader_data_bytes
