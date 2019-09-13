from dxbc.legacy.exprs import ChoiceExpr
from dxbc.legacy.exprs import Expr


class ValueExpr(Expr):
    @staticmethod
    def create(str_data):
        from dxbc.legacy.exprs import ImmediateExpr
        from dxbc.legacy.exprs import SwizzleExpr
        return ChoiceExpr(ImmediateExpr, SwizzleExpr).create(str_data)

    def __init__(self, str_data, values):
        Expr.__init__(self, str_data)
        if not values:
            raise ValueError("Expected ValueExpr to have values")
        self.values = list(values)
        self.value_count = len(values)

    def __getitem__(self, index):
        raise NotImplementedError()

    def mask(self, mask_values_out):
        raise NotImplementedError()
