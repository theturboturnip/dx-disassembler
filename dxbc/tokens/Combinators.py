from typing import Type, List

from dxbc.Errors import DXBCTokenizeError, DXBCError
from dxbc.tokens.Base import Token, EatReturnType
from utils import list_str, reraise


def CompoundToken(*token_types: Type[Token]):
    class CompoundToken_Impl(Token):
        @staticmethod
        def eat(str_data) -> EatReturnType:
            tokens = []
            remaining_data = str_data
            for i, token_type in enumerate(token_types):
                try:
                    new_token_list, remaining_data = token_type.eat(remaining_data)
                    tokens += new_token_list
                except DXBCError as e:
                    token_str = str(token_types).replace("{", "{{").replace("}", "}}")
                    reraise(e, f"Error extracting token {i} from {token_str}:\n\t{{}}")
            return tokens, remaining_data
    return CompoundToken_Impl


def OptionalToken(optional_token_type: Type[Token]):
    @staticmethod
    def eat(str_data) -> EatReturnType:
        try:
            return optional_token_type.eat(str_data)
        except DXBCTokenizeError as e:
            return [], str_data

    return type(f"Optional_{optional_token_type}", (Token,), {
        "eat": eat
    })

def FirstOfTokens(*token_types: [Type[Token]]):
    class FirstOfTokens_Impl(Token):
        @staticmethod
        def eat(str_data) -> EatReturnType:
            for i, token_type in enumerate(token_types):
                try:
                    return token_type.eat(str_data)
                except DXBCTokenizeError as e:
                    #print(f"Error extracting token {i} from {token_types}:\n\t{{}}")
                    continue
            raise DXBCTokenizeError("Couldn't match any of {}", list_str(token_types))
    return FirstOfTokens_Impl


def RepeatingToken(token_type: Type[Token], min_repeats: int = 0, max_repeats: int = -1):
    class RepeatingToken_Impl:
        @staticmethod
        def eat(str_data) -> EatReturnType:
            tokens = []
            remaining_data = str_data
            reps = 0
            while True:
                try:
                    new_token_list, remaining_data = token_type.eat(remaining_data)
                except DXBCTokenizeError as e:
                    #print (e)
                    break
                tokens += new_token_list
                reps += 1
            if reps < min_repeats or (reps > max_repeats > 0):
                raise DXBCTokenizeError("Token {} should have repeated between {} and {} times, actually repeated {}".format(token_type, min_repeats, max_repeats, reps))

            return tokens, remaining_data

    return RepeatingToken_Impl


def SequenceToken_init(self, token_list: List[Token]):
    Token.__init__(self, "".join([x.str_data for x in token_list]))
    self.tokens = token_list


def SequenceToken(*token_type_list: List[Type[Token]]):
    # Create the type without the eat() function, because it has to reference this type later
    sequence_base_token_type = type("SequenceToken_Impl", (Token,), {
        "__init__": SequenceToken_init,
        "__repr__": lambda self: f"<SequenceToken_Impl: {self.tokens}>",
        "token_type_list": token_type_list
    })

    ct_eat = CompoundToken(*token_type_list).eat
    @classmethod
    def eat(cls: Type, str_data:str) -> EatReturnType:
        token_list, remaining = ct_eat(str_data)
        return [cls(token_list)], remaining

    sequence_base_token_type.eat = eat
    return sequence_base_token_type
