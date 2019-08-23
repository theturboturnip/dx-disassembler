import dxbc
from dxbc.Instruction import *
from dxbc.InstructionMap import getInstructionType
from dxbc.tokens import *
from dxbc.exprs import *
from shader_source import instruction_str


def list_str(list):
    return ", ".join([str(x) for x in list])


CT = CompoundToken
OT = OptionalToken

value_expr_token = ExpressionToken(ValueExpr)
arguments_token = OT(CT(ExpressionToken(SwizzleOutputExpr), RepeatingToken(CT(RegexToken(","), WhitespaceToken, value_expr_token))))
instruction_token = CT(WhitespaceToken, LineNumberToken, WhitespaceToken,
                       InstructionNameToken, WhitespaceToken, arguments_token, OT(NewlineToken))

print(SwizzleOutputExpr)

# test_token = RepeatingToken(CT(RegexToken(r"\d+"), OT(CT(RegexToken(","), WhitespaceToken))))
# print(", ".join([str(x) for x in test_token.eat("1,2,3,4,5,")[0]]))
# print(list_str(test_token.eat("1, 2, 3, 4, 5")[0]))
# print(list_str(value_expr_token.eat("r0.y")[0]))

from shader_source import instruction_str

#instructions = filter(lambda x: x, [x.lstrip() for x in instruction_str.split("\n")])
#for instr in instructions:
#    print(instr)
#    tokens, remaining = instruction_token.eat(instr)
#    print("{}, rem: {}".format(list_str(tokens), repr(remaining)))

remaining = instruction_str
while True:
    try:
        tokens, remaining = instruction_token.eat(remaining)
        #print(list_str(tokens))
    except ValueError as e:
        print(e)
        break

    instr_name, args_exprs = extract_instruction_data(tokens)
    print(getInstructionType(instr_name)(instr_name, args_exprs).disassemble())
    #print("instr: {}, args: {}".format(instr_name, list_str(args_exprs)))
    #if instr_name == "sample_indexable(texture2d)(float,float,float,float)":
        #print(list_str(tokens))
    #    print(SampleTexInstruction(instr_name, args_exprs).disassemble())
    #else:
    #    print(ArithmeticInstruction(instr_name, args_exprs).disassemble())
    #print("{} rem {}".format(list_str(tokens), repr(remaining[0:10])))