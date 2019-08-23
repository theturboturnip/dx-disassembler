import dxbc
from dxbc.Instruction import *
from dxbc.InstructionMap import getInstructionType
from dxbc.tokens import *
from dxbc.exprs import *
from utils import *


CT = CompoundToken
OT = OptionalToken

value_expr_token = ExpressionToken(ValueExpr)
arguments_token = OT(CT(ExpressionToken(SwizzleOutputExpr), RepeatingToken(CT(RegexToken(","), WhitespaceToken, value_expr_token))))
instruction_token = CT(WhitespaceToken, LineNumberToken, WhitespaceToken,
                       InstructionNameToken, WhitespaceToken, arguments_token, OT(NewlineToken))

from shader_source import ps_instruction_str2 as instruction_str

remaining = instruction_str
while True:
    try:
        tokens, remaining = instruction_token.eat(remaining)
        #print(list_str(tokens))
    except ValueError as e:
        print(e)
        break

    try:
        instr_name, args_exprs = extract_instruction_data(tokens)
        instr = getInstructionType(instr_name)(instr_name, args_exprs)
    except ValueError as e:
        reraise(e, "{} encountered when disassembling " + list_str(tokens))
    print(instr.disassemble())