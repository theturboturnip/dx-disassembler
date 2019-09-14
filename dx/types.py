import ctypes


class D3D_SHADER_MACRO(ctypes.Structure):
    pass


class ID3D_Include(ctypes.Structure):
    pass


"""typedef struct ID3D10BlobVtbl
    {
        BEGIN_INTERFACE

        HRESULT ( STDMETHODCALLTYPE *QueryInterface )( 
            ID3D10Blob * This,
            /* [in] */ REFIID riid,
            /* [annotation][iid_is][out] */ 
            _COM_Outptr_  void **ppvObject);

        ULONG ( STDMETHODCALLTYPE *AddRef )( 
            ID3D10Blob * This);

        ULONG ( STDMETHODCALLTYPE *Release )( 
            ID3D10Blob * This);

        LPVOID ( STDMETHODCALLTYPE *GetBufferPointer )( 
            ID3D10Blob * This);

        SIZE_T ( STDMETHODCALLTYPE *GetBufferSize )( 
            ID3D10Blob * This);

        END_INTERFACE
    } ID3D10BlobVtbl;

    interface ID3D10Blob
    {
        CONST_VTBL struct ID3D10BlobVtbl *lpVtbl;
    };"""


class ID3D10Blob(ctypes.Structure):
    pass


class ID3D10Blob_VTable(ctypes.Structure):
    _fields_ = [
        ("QueryInterface", ctypes.c_void_p),
        ("AddRef", ctypes.WINFUNCTYPE(
            ctypes.c_ulong,
            ctypes.POINTER(ID3D10Blob))
         ),
        ("Release", ctypes.WINFUNCTYPE(
            ctypes.c_ulong,
            ctypes.POINTER(ID3D10Blob))
         ),
        ("GetBufferPointer", ctypes.WINFUNCTYPE(
            ctypes.c_void_p,
            ctypes.POINTER(ID3D10Blob))
         ),
        ("GetBufferSize", ctypes.WINFUNCTYPE(
            ctypes.c_size_t,
            ctypes.POINTER(ID3D10Blob))
         ),
    ]


ID3D10Blob._fields_ = [("vtable", ctypes.POINTER(ID3D10Blob_VTable))]