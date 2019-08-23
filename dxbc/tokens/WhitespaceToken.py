from dxbc.tokens import RegexToken
from dxbc.tokens.Token import Token


class WhitespaceToken(Token):
    @staticmethod
    def eat(str_data):
        return RegexToken(r"\s*", token_type=WhitespaceToken).eat(str_data)
        #new_data = str_data.lstrip()
        #eaten_data = str_data[0:len(new_data)]
        #return [WhitespaceToken(eaten_data)], new_data

    def __init__(self, str_data):
        Token.__init__(self, str_data)
