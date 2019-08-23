from dxbc.tokens import *
from dxbc.exprs import *

class Instruction:
    def __init__(self, token, arguments):
        self.token = token
        self.arguments = arguments

    #@staticmethod
    #def owns_tokens(tokens):
    #    raise NotImplementedError()

    def disassemble(self):
        raise NotImplementedError()

    def __str__(self):
        return self.disassemble()

class ReturnInstruction(Instruction):
    def __init__(self, token, args):
        if len(args) > 0:
            raise ValueError("Return Instruction shouldn't have arguments")
        Instruction.__init__(self, token, args)

    def disassemble(self):
        return "return;"

class ResultInstruction(Instruction):
    def __init__(self, token, args):
        if len(args) == 0:
            raise ValueError("Result Instruction should have at least one argument")
        if not isinstance(args[0], SwizzleOutputExpr):
            raise ValueError("Output of Result Instruction must be a SwizzleOutputExpr")
        self.result_arg = args[0]
        self.calc_args = args[1:]
        Instruction.__init__(self, token, args)
        self.value_mask = self.result_arg.output_mask

    def disassemble(self):
        return "{} {} {};".format(self.token, self.result_arg, ", ".join([str(x) for x in self.calc_args]))

class SampleTexInstruction(ResultInstruction):
    def __init__(self, token, args):
        ResultInstruction.__init__(self, token, args)

        #def list_str(list):
        #    return ", ".join([str(x) for x in list])
        #print(list_str(self.calc_args))
        self.uv_arg = self.calc_args[0].mask([True, True, False, False]) # UVs are X,Y
        self.texture_arg = self.calc_args[1].mask(self.value_mask)
        if isinstance(self.texture_arg, ImmediateExpr):
            raise ValueError("Texture expr must not be an immediate")
        self.sampler_arg = self.calc_args[2].mask([False] * len(self.calc_args[2].values)) # Make sure only one argument remains

    def disassemble(self):
        return "{} = {}.Sample({}, {}).{};".format(self.result_arg, self.texture_arg.var, self.sampler_arg.var, self.uv_arg, "".join(self.texture_arg.values))

class ArithmeticInstruction(ResultInstruction):
    def __init__(self, token, args, trunc_args=True, trunc_len=0):
        ResultInstruction.__init__(self, token, args)

        expected_argcount = sum(self.value_mask)
        if trunc_args:
            masked_calc_args = []
            for arg in self.calc_args:
                if trunc_len > 0:
                    mask = [True] * trunc_len + [False] * (4 - trunc_len)
                    masked_calc_args.append(arg.mask(mask))
                elif expected_argcount > arg.value_count:
                    raise ValueError("Expected at least %d arg values, got %d" % (expected_argcount, sum(arg.value_mask)))
                elif expected_argcount < arg.value_count:
                    masked_calc_args.append(arg.mask(self.value_mask))
                else:
                    masked_calc_args.append(arg)
            self.calc_args = masked_calc_args

class BinaryArithmeticInstruction(ArithmeticInstruction):
    def __init__(self, token, args, sep):
        ArithmeticInstruction.__init__(self, token, args)
        if len(self.calc_args) != 2:
            raise ValueError("Binary Arithmetic Instruction must have exactly 2 arguments")
        self.sep = sep

    def disassemble(self):
        return "{} = {} {} {};".format(self.result_arg, self.calc_args[0], self.sep, self.calc_args[1])

class FuncInstruction(ArithmeticInstruction):
    def __init__(self, token, args, f, trunc_args=True, trunc_len=0):
        ArithmeticInstruction.__init__(self, token, args, trunc_args, trunc_len)
        self.f = f

    def disassemble(self):
        return "{} = {}({});".format(self.result_arg, self.f, ", ".join([str(x) for x in self.calc_args]))

class MoveInstruction(ArithmeticInstruction):
    def disassemble(self):
        return "{} = {};".format(self.result_arg, self.calc_args[0])

class MoveCondInstruction(ArithmeticInstruction):
    def disassemble(self):
        return "{} = (uint){} ? {} : {};".format(self.result_arg, self.calc_args[0], self.calc_args[1], self.calc_args[2])

class BitfieldInsert(ArithmeticInstruction):
    def disassemble(self):
        return "{{ uint mask = 0xffffffff >> (32 - {0}); {2} = (({3} << {1}) & mask) | ({4} & ~mask); }}".format(
            self.calc_args[0], self.calc_args[1], self.result_arg, self.calc_args[2], self.calc_args[3]
        )

class MADDInstruction(ArithmeticInstruction):
    def disassemble(self):
        return "{} = ({} * {}) + {};".format(self.result_arg, self.calc_args[0], self.calc_args[1], self.calc_args[2])

class DiscardNZInstruction(ResultInstruction):
    def disassemble(self):
        return "if ({} != 0) {{ discard; }}".format(self.result_arg)

def extract_instruction_data(tokens):
    tokens = list(filter(lambda x: not isinstance(x, (WhitespaceToken, NewlineToken, RegexToken_Impl)), tokens))
    instr_tokens = list(filter(lambda x: isinstance(x, InstructionNameToken), tokens))
    arg_tokens = list(filter(lambda x: isinstance(x, ExpressionToken_Impl), tokens))
    arg_exprs = list(map(lambda x: x.expr, arg_tokens))

    if len(instr_tokens) != 1:
        raise ValueError("Expected 1 InstructionNameToken, got {}".format(len(instr_tokens)))

    return instr_tokens[0].str_data, arg_exprs