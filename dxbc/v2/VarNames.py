from dxbc.v2.Base import ScalarValueBase


class VarNameBase:
    name: str

    def __init__(self, name: str):
        super().__init__()
        self.name = name

    def disassemble(self) -> str:
        return self.name

    def __str__(self):
        return self.disassemble()

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self.name == other.name


class IndexedVarName(VarNameBase):
    # These are summed to get the final offset, allowing variable vector components to be used.
    indices: [ScalarValueBase]

    def __init__(self, name: str, indices: [ScalarValueBase]):
        super().__init__(name)
        self.indices = indices

    def disassemble(self) -> str:
        return "{}[{}]".format(self.name, " ".join([str(x) for x in self.indices]))

    def __eq__(self, other):
        return (super().__eq__(other)
                and self.indices == other.indices)


