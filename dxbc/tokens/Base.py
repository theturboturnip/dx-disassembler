import re
from typing import Tuple, Callable, List

from dxbc.Errors import DXBCTokenizeError


class Token:
    def __init__(self, str_data):
        self.str_data = str_data

    @staticmethod
    def eat(str_data):
        raise NotImplementedError

    def __str__(self):
        return "{0}({1})".format(type(self).__name__, repr(self.str_data))

EatReturnType = Tuple[List[Token], str]

def RegexToken(regex_str: str, name:str):
    # Create the type without the eat() function, because it has to reference this type later
    regex_token_type = type("{}_Impl".format(name), (Token,), {})
    @staticmethod
    def eat(str_data) -> EatReturnType:
        match = re.match(regex_str, str_data)
        if match is None:
            raise DXBCTokenizeError("Couldn't tokenize RegEx \"{}\" from sequence \"{}\"".format(regex_str, str_data[:10]))
        return [regex_token_type(match.group(0))], str_data[len(match.group(0)):]
    regex_token_type.eat = eat
    return regex_token_type
