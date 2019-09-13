class Expr:
    def __init__(self, str_data):
        self.str_data = str_data

    @staticmethod
    def create(str_data):
        raise NotImplementedError()