from abc import ABC
from enum import Enum
from typing import Union, List

from dxbc.Errors import DXBCError
from dxbc.v2.Types import VectorType, ScalarType
from dxbc.v2.values import ScalarValueBase, Value, VectorValueBase, mask_components, trim_components

GenericValue = Value
GenericValueType = Union[ScalarType, VectorType]


class ArgumentTruncation:
    input_types: List[GenericValueType]
    output_type: GenericValueType

    def truncate_args(self, input_args: List[GenericValue], output_arg: GenericValue):
        """
        Creates a copy of input_args, truncates the values as it desires,
        and ends.
        """
        raise NotImplementedError()

class NullTruncate(ArgumentTruncation):
    def truncate_args(self, input_args, output_arg):
        return input_args


class TruncateToOutput(ArgumentTruncation):
    def truncate_args(self, input_args, output_arg):
        output_mask = output_arg.get_output_mask()
        return [mask_components(arg, output_mask) for arg in input_args]

class TruncateToLength(ArgumentTruncation, ABC):
    pass

def makeTruncateToLength(length: int):
    class TruncateToLength_Impl(TruncateToLength):
        def truncate_args(self, input_args, output_arg):
            return [trim_components(arg, length) for arg in input_args]
    return TruncateToLength_Impl


class Function:
    name: str
    input_types: List[GenericValueType]
    output_type: GenericValueType

    def __init__(self, name, input_types, output_type):
        if not isinstance(self, ArgumentTruncation):
            raise DXBCError("Function must have some form of argument truncation")


def get_closest_types(value: Value) -> GenericValueType:
    if isinstance(value, ScalarValueBase):
        return value.scalar_type
    elif isinstance(value, VectorValueBase):
        return VectorType(value.scalar_type, value.num_components)