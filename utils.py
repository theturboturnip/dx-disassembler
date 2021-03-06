import sys
from copy import copy
from typing import Type, List

from dxbc.Errors import DXBCValueError, DXBCError


def list_str(l):
    return ", ".join([str(x) for x in l])


def dict_str(d):
    return ", ".join(["{}: {}".format(str(k), str(v)) for (k, v) in d.items()])


def reraise(e, extra):
    #err = copy(e)
    #err.message = extra.format(str(e))
    if len(sys.exc_info()) >= 3:
        raise type(e)(extra.format(str(e))).with_traceback(sys.exc_info()[2])
    else:
        raise type(e)(extra.format(str(e)))


def FirstPossibleOf(types: List[Type], potential_errors: List[Type[Exception]] = None):
    """
    Returns a type that when created will return a value of the first type
    which doesn't throw one of the potential_errors during creation.
    :param types:
    :param potential_errors:
    :return:
    """
    if potential_errors is None:
        potential_errors = [DXBCError]

    class AnyType:
        def __new__(cls, *args, **kwargs):
            error_string = ""
            for t in types:
                try:
                    return t(*args, **kwargs)
                except tuple(potential_errors) as e:
                    error_string += "\tCouldn't create {}: {}\n".format(t, str(e).replace("\n", "\n\t"))

            # At this point we know none of the types could be created
            error_string = "Failed creating any of [{}] with args=[{}], kwargs={{ {} }}:\n".format(
                list_str(types), list_str(args), dict_str(kwargs)) + error_string
            raise DXBCError(error_string)

    return AnyType
