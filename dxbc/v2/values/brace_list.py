from dxbc.v2.values import Value


class BraceList:
    str_data: str

    def __init__(self, str_data: str):
        self.str_data = str_data

    def __str__(self):
        return self.str_data