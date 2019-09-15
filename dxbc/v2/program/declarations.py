import collections
import typing
from enum import IntEnum
from typing import List, Dict, Union

from dxbc.Errors import DXBCError
from dxbc.v2.values import Value
from dxbc.v2.values.brace_list import BraceList


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

Declaration = typing.NamedTuple("declaration", [("config_list", List[Value]),  ("value_list", List[Value])])

class DeclStorage:
    normal_storage: Dict[DeclName, List[Declaration]]
    icb_buffers: List[BraceList]

    def __init__(self):
        self.normal_storage = {
            d: [] for d in DeclName if d is not DeclName.ImmediateBufferToken
        }
        self.icb_buffers = []

    def __str__(self):
        str_dict = {DeclName.ImmediateBufferToken: self.icb_buffers}
        str_dict.update(self.normal_storage)
        return str(str_dict)

    def __getitem__(self, item: DeclName) -> List[Declaration]:
        if item is DeclName.ImmediateBufferToken:
            raise DXBCError("Can't index DeclStorage for ImmediateBufferToken, use .icb_buffers instead")
        return self.normal_storage[item]
