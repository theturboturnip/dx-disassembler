class DXBCError(Exception):
    pass


class DXBCValueError(DXBCError):
    pass


class DXBCTokenizeError(DXBCError):
    pass


class DXBCInstructionDecodeError(DXBCError):
    pass