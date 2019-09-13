from enum import IntEnum


class DeclName(IntEnum):
    GlobalFlags = 0,
    ImmediateBufferToken = 1,
    ConstantBufferToken = 2,
    SamplerToken = 3,
    TextureToken = 4,
    TypedPSInput = 5,
    UntypedInput = 6,
    Output = 7,
    RegisterCount = 8