from dxbc.tokens.Token import Token


class NewlineToken(Token):
    def __init__(self, str_data):
        Token.__init__(self, str_data)

    @staticmethod
    def eat(str_data):
        if len(str_data) == 0 or str_data[0] != '\n':
            raise ValueError()
        return [NewlineToken(str_data[0:1])], str_data[1:]