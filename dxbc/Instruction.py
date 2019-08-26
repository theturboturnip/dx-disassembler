from dxbc.Errors import DXBCInstructionDecodeError
from dxbc.tokens import *
from dxbc.exprs import *
from dxbc.tokens.Lang import InstructionNameToken
from dxbc.v2.values import *
from dxbc.v2.values.tokens import ValueHoldingToken


class Instruction:
    def __init__(self, token, arguments):
        self.token = token
        self.arguments = arguments

    # @staticmethod
    # def owns_tokens(tokens):
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
    def __init__(self, token, args: List[Value]):
        if len(args) == 0:
            raise ValueError("Result Instruction should have at least one argument")
        self.result_arg = args[0]
        self.calc_args = args[1:]
        Instruction.__init__(self, token, args)
        self.output_mask = self.result_arg.get_output_mask()

    def disassemble(self):
        return "{} {} {};".format(self.token, self.result_arg, ", ".join([str(x) for x in self.calc_args]))


class SampleTexInstruction(ResultInstruction):
    uv_arg: VectorValueBase
    texture_arg: VectorValueBase
    sampler_arg: VarNameBase

    def __init__(self, token, args):
        ResultInstruction.__init__(self, token, args)

        # def list_str(list):
        #    return ", ".join([str(x) for x in list])
        # print(list_str(self.calc_args))
        self.uv_arg = trim_components(self.calc_args[0], 2) # UVs are X,Y
        self.texture_arg = mask_components(self.calc_args[1], self.output_mask)
        if isinstance(self.texture_arg, ImmediateExpr):
            raise ValueError("Texture expr must not be an immediate")
        self.sampler_arg = self.calc_args[2].scalar_name

    def disassemble(self):
        return "{} = {}.Sample({}, {}).{};".format(self.result_arg, self.texture_arg.vector_name, self.sampler_arg,
                                                   self.uv_arg, "".join(c.name for c in self.texture_arg.components))


class ArithmeticInstruction(ResultInstruction):
    def __init__(self, token, args, trunc_args=True, trunc_len=0):
        ResultInstruction.__init__(self, token, args)

        expected_argcount = sum(self.output_mask)
        if trunc_args:
            masked_calc_args = []
            for arg in self.calc_args:
                if trunc_len > 0:
                    #mask = [True] * trunc_len + [False] * (4 - trunc_len)
                    masked_calc_args.append(trim_components(arg, trunc_len))#arg.mask(mask))
                elif expected_argcount > arg.num_components:
                    raise ValueError(
                        "Expected at least %d arg values, got %d" % (expected_argcount, arg.num_components))
                elif expected_argcount < arg.num_components:
                    masked_calc_args.append(mask_components(arg, self.output_mask))
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
        return "{} = (uint){} ? {} : {};".format(self.result_arg, self.calc_args[0], self.calc_args[1],
                                                 self.calc_args[2])


class BitfieldInsert(ArithmeticInstruction):
    def disassemble(self):
        return "{{ uint mask = (0xffffffff >> (32 - {0})) << {1}; {2} = (({3} << {1}) & mask) | ({4} & ~mask); }}".format(
            self.calc_args[0], self.calc_args[1], self.result_arg, self.calc_args[2], self.calc_args[3]
        )


class MADDInstruction(ArithmeticInstruction):
    def disassemble(self):
        return "{} = ({} * {}) + {};".format(self.result_arg, self.calc_args[0], self.calc_args[1], self.calc_args[2])


class DiscardNZInstruction(ResultInstruction):
    def disassemble(self):
        return "if ({} != 0) {{ discard; }}".format(self.result_arg)