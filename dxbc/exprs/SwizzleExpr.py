import re

from dxbc.exprs import Expr
from dxbc.exprs.ValueExpr import ValueExpr

# TODO Variable-aware array indexing
full_regex = re.compile(r"(" +  # First group, holds variable to swizzle
                        r"[+-]?[\w\d]+" + r"(?:\[[^\]]+\])?" +  # Capture minus, variable name, optionally capture array indexer
                        r")" +
                        r"(?:\.([xyzw]{1,4}))?"  # Optionally capture XYZW swizzle
                        )


class SwizzleExpr(ValueExpr):
    @staticmethod
    def create(str_data):
        match = full_regex.match(str_data)
        if match is None:
            raise ValueError()

        return SwizzleExpr(str_data, match.group(1), match.group(2))

    def __init__(self, str_data, var, swizzle_comps):
        if not swizzle_comps:
            swizzle_comps = "x"
        ValueExpr.__init__(self, str_data, swizzle_comps)
        self.var = var
        self.swizzle_comps = swizzle_comps
        if not swizzle_comps:
            self.value_mask = [True, False, False, False]  # X only
        else:
            self.value_mask = [
                'x' in swizzle_comps,
                'y' in swizzle_comps,
                'z' in swizzle_comps,
                'w' in swizzle_comps,
            ]

    def __getitem__(self, item):
        if not self.swizzle_comps:
            raise IndexError()
        return self.var + "." + self.swizzle_comps[item]

    def mask(self, mask_values_out):
        if len(self.values) > len(mask_values_out):
            raise ValueError("Tried to mask a {}-component value with {}-component mask".format(len(self.values), len(mask_values_out)))
        return SwizzleExpr("<autogenerated>",
                           self.var,
                           [self.values[i] for i,v in enumerate(self.values) if mask_values_out[i]])

    def __str__(self):
        if (all(x == self.values[0] for x in self.values)):
            return "{}.{}".format(self.var, self.values[0])
        return "{}.{}".format(self.var, "".join(self.values))#self.str_data


class SwizzleOutputExpr(Expr):
    @staticmethod
    def create(str_data):
        match = full_regex.match(str_data)
        if match is None:
            raise ValueError()

        return SwizzleOutputExpr(str_data, match.group(1), match.group(2))

    def __init__(self, str_data, var, swizzle_comps):
        if not swizzle_comps:
            self.output_mask = [True, False, False, False] # X only
        else:
            self.output_mask = [
                'x' in swizzle_comps,
                'y' in swizzle_comps,
                'z' in swizzle_comps,
                'w' in swizzle_comps,
            ]
        self.value_mask = self.output_mask
        Expr.__init__(self, str_data)
        self.var = var
        self.swizzle_comps = swizzle_comps

    def __str__(self):
        if self.swizzle_comps:
            return "{}.{}".format(self.var, self.swizzle_comps)
        return self.var