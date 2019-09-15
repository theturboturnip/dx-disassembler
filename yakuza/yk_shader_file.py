import abc
from pathlib import WindowsPath
from typing import Union, overload, List

from utils import FirstPossibleOf, reraise


def import_yakuza_shader_file(path: WindowsPath) -> 'YkShaderFile':
    byte_data = None
    with path.open("rb") as f:
        byte_data = bytearray(f.read())
    if not byte_data or len(byte_data) < 4:
        raise YkError(f"Couldn't open {path} and extract >4 bytes.")

    return FirstPossibleOf([YkPixelShaderFile, YkEffectShaderFile], [YkError])(byte_data)

class YkError(Exception):
    pass

HEADER_SIZE = 0x80

class YkShaderFile(abc.ABC):
    DATA_LENGTH_OFFSETS_FROM_HEADER: List[int]
    expected_header: str
    byte_data: bytearray
    offset: int
    data_length: int

    def __init__(self, byte_data: bytearray, offset: int = 0):
        self.byte_data = byte_data
        self.offset = offset
        header = self[:4]
        if header != self.expected_header.encode("utf-8"):
            raise YkError(f"Invalid file header, expected {self.expected_header} but got {header}")

        data_lengths = []
        for length_offset in self.DATA_LENGTH_OFFSETS_FROM_HEADER:
            data_lengths.append(self.get_int(length_offset, 2))
        if not all(l == data_lengths[0] for l in data_lengths):
            raise YkError(f"Expected data lengths to match, got {[hex(x) for x in data_lengths]}")
        self.data_length = data_lengths[0]

        if self.offset + self.data_length > len(self.byte_data):
            raise YkError(f"offset + data_length is longer than the actual data! "
                          f"expected end: {self.offset + self.data_length}, data length: {len(self.byte_data)}")

    def get_int(self, address: int, byte_length: int):
        return int.from_bytes(self[address:address + byte_length], "little")

    def set_int(self, address: int, byte_length: int, value: int):
        self[address:address + byte_length] = value.to_bytes(byte_length, "little")

    @overload
    def __getitem__(self, item: int) -> int:
        pass

    @overload
    def __getitem__(self, item: slice) -> bytearray:
        pass

    def __getitem__(self, item: Union[slice, int]):
        if item is int:
            return self.byte_data[item + self.offset]
        return self.byte_data[self.offset + (item.start or 0):self.offset + (item.stop or -1):(item.step or 1)]

    @overload
    def __setitem__(self, key: int, value: int):
        pass

    @overload
    def __setitem__(self, key:slice, value: Union[bytes, bytearray]):
        pass

    def __setitem__(self, key: Union[int, slice], value: Union[int, bytes, bytearray]):
        if isinstance(key, slice):
            self.byte_data[self.offset + (key.start or 0):self.offset + (key.stop or -1):(key.step or 1)] = value
        else:
            self.byte_data[key] = value

    def get_pixel_shader_data(self) -> bytes:
        raise NotImplementedError()

class YkPixelShaderFile(YkShaderFile):
    expected_header = "GSPS"
    DATA_LENGTH_OFFSETS_FROM_HEADER = [0x0C, 0x1C]

    def __init__(self, byte_data: bytearray, offset: int = 0):
        super().__init__(byte_data, offset)

class YkEffectShaderFile(YkShaderFile):
    expected_header = "GSFX"
    DATA_LENGTH_OFFSETS_FROM_HEADER = [0x0C]
    pixel_shader_file: YkPixelShaderFile

    PIXEL_SHADER_ADDRESS_OFFSET = 0x38
    PIXEL_SHADER_LENGTH_OFFSET = 0x3C

    def __init__(self, byte_data: bytearray, offset: int = 0):
        super().__init__(byte_data, offset)
        pixel_shader_address = self.get_int(self.PIXEL_SHADER_ADDRESS_OFFSET, 2)
        pixel_shader_length = self.get_int(self.PIXEL_SHADER_LENGTH_OFFSET, 2)

        try:
            self.pixel_shader_file = YkPixelShaderFile(self.byte_data, self.offset + pixel_shader_address)
        except YkError as e:
            reraise(e, f"Error while constructing pixel shader file:" + "\n{}")

        actual_data_length = self.pixel_shader_file.data_length + HEADER_SIZE
        if actual_data_length != pixel_shader_length:
            raise YkError(f"Expected pixel shader data to be of "
                          f"length {pixel_shader_length:x}, header says {actual_data_length:x}")