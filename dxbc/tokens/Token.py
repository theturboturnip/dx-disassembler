class Token:
    def __init__(self, str_data):
        self.str_data = str_data

    @staticmethod
    def eat(str_data):
        raise NotImplementedError

    def __str__(self):
        return "{0}({1})".format(type(self).__name__, repr(self.str_data))