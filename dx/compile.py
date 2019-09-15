from dx.errors import DXCallError
from dx.types import *
from dx.dll import d3d11_compile_shader

def compile_shader(src_shader: str, file_name: str, flags: int = 0, entry_point: str = "main", compile_target: str = "ps_5_0") -> bytes:
    b_src_shader = src_shader.encode("utf-8")
    b_file_name = file_name.encode("utf-8")
    b_entry_point = entry_point.encode("utf-8")
    b_compile_target = compile_target.encode("utf-8")

    blob_ptr_type = ctypes.POINTER(ID3D10Blob)
    shader_data_blob = blob_ptr_type()
    error_data_blob = blob_ptr_type()

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
        raise we
    finally:
        if result or error_data_blob:
            error_bytes = blob_to_bytes(error_data_blob)
            error_str = str(error_bytes, "utf-8")
            error_data_blob.contents.vtable.contents.Release(error_data_blob)

            raise DXCallError(f"Error in contents:\n{src_shader}\n{error_str}")
    shader_data_bytes = blob_to_bytes(shader_data_blob)
    shader_data_blob.contents.vtable.contents.Release(shader_data_blob)
    return shader_data_bytes
