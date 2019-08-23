import re

from dxbc.tokens.Token import Token


class RegexToken_Impl(Token):
    def __init__(self, str_data):
        Token.__init__(self, str_data)


class RegexToken:
    def __init__(self, regex_str, token_type=RegexToken_Impl):
        self.regex = re.compile(regex_str)
        self.token_type = token_type

    def eat(self, str_data):
        match = self.regex.match(str_data)
        if match is None:
            raise ValueError
        return [self.token_type(match.group(0))], str_data[len(match.group(0)):]
