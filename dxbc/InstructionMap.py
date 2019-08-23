from dxbc.Instruction import *

__all__ = ["getInstructionType"]

def makeBinaryInstruction(sep):
    class BinaryInstruction(BinaryArithmeticInstruction):
        def __init__(self, token, args):
            BinaryArithmeticInstruction.__init__(self, token, args, sep)

    return BinaryInstruction

def makeFuncInstruction(f, trunc_args = True):
    class MyFuncInstruction(FuncInstruction):
        def __init__(self, token, args):
            FuncInstruction.__init__(self, token, args, f, trunc_args)

    return MyFuncInstruction

instruction_map = {
    "sample_indexable(texture2d)(float,float,float,float)": SampleTexInstruction,

    "add": makeBinaryInstruction('+'),
    "iadd": makeBinaryInstruction('i+'),
    "mul": makeBinaryInstruction('*'),
    "div": makeBinaryInstruction('/'),
    "or": makeBinaryInstruction('|'),
    "and": makeBinaryInstruction('&'),
    "xor": makeBinaryInstruction('^'),
    "mov": MoveInstruction,
    "movc": MoveCondInstruction,
    "mad": MADDInstruction,
    "lt" : makeBinaryInstruction('<'),
    "ine": makeBinaryInstruction("i!="),
    "ne": makeBinaryInstruction("!="),
    "eq": makeBinaryInstruction("=="),
    "ieq": makeBinaryInstruction("i=="),
    "ishl": makeBinaryInstruction("i<<"),

    "max": makeFuncInstruction("max"),
    "min": makeFuncInstruction("min"),
    "sqrt": makeFuncInstruction("sqrt"),
    "rsq": makeFuncInstruction("1/sqrt"),
    "f16tof32": makeFuncInstruction("f32"),
    "ftou": makeFuncInstruction("uint"),
    "sqrt": makeFuncInstruction("sqrt"),
    "dp2": makeFuncInstruction("dot2", trunc_args=False),
    "dp3": makeFuncInstruction("dot3", trunc_args=False),

    "bfi":BitfieldInsert,

    "ret": ReturnInstruction
}
def getInstructionType(instr_name):
    if instr_name in instruction_map:
        return instruction_map[instr_name]
    return ArithmeticInstruction