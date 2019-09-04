class VarNameBase:
    name: str

    def __init__(self, name: str):
        super().__init__()
        self.name = name

    def as_base(self) -> 'VarNameBase':
        return self

    def disassemble(self) -> str:
        return self.name

    def __hash__(self):
        return hash(repr(self))

    def __str__(self):
        return self.disassemble()

    def __repr__(self):
        return f"VarNameBase {self.name}"

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self.name == other.name


class IndexedVarName(VarNameBase):
    # These are summed to get the final offset, allowing variable vector components to be used.
    indices: ['ScalarValueBase']

    def __init__(self, name: str, indices: ['ScalarValueBase']):
        super().__init__(name)
        self.indices = indices

    def disassemble(self) -> str:
        return "{}[{}]".format(self.name, " + ".join([str(x) for x in self.indices]))

    def as_base(self):
        return VarNameBase(self.name)

    def __repr__(self):
        return f"IndexedVarName {self.name} {self.indices}"

    def __eq__(self, other):
        return (super().__eq__(other))
                #and self.indices == other.indices)


