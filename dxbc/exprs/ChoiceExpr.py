from dxbc.exprs.Expr import Expr


class ChoiceExpr(Expr):
    def __init__(self, *token_types):
        self.token_types = token_types

    def create(self, str_data):
        for token_type in self.token_types:
            try:
                return token_type.create(str_data)
            except ValueError:
                pass
        raise ValueError("Token {0} doesn't match any type in list {1}".format(str_data, self.token_types))