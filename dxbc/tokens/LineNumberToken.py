import re

from dxbc.tokens.Token import Token

line_number_regex = re.compile(r"^(\d+):")


class LineNumberToken(Token):
    def __init__(self, str_data, line_number):
        Token.__init__(self, str_data)
        self.line_number = line_number

    @staticmethod
    def eat(str_data):
        match = line_number_regex.match(str_data)
        if match is None:
            raise ValueError
        return [LineNumberToken(match.group(0), int(match.group(1)))], str_data[len(match.group(0)):]

    def __str__(self):
        return super().__str__()