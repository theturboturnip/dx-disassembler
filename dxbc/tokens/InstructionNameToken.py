from dxbc.tokens.RegexToken import RegexToken
from dxbc.tokens.Token import Token


class InstructionNameToken(Token):
    def __init__(self, str_data):
        Token.__init__(self, str_data)

    @staticmethod
    def eat(str_data):
        return RegexToken(r"[^\s]+", token_type=InstructionNameToken).eat(str_data)