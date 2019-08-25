from dxbc.Instruction import *
from dxbc.InstructionMap import getInstructionType
from dxbc.tokens import *
from dxbc.v2.values.tokens import ValueToken
from utils import *


CT = CompoundToken
OT = OptionalToken

value_expr_token = ValueToken#ExpressionToken(ValueExpr)
arguments_token = OT(CT(
    value_expr_token,
    #ExpressionToken(SwizzleOutputExpr),
    RepeatingToken(
        CT(RegexToken(",", "comma"), WhitespaceToken, value_expr_token)
    )
))
instruction_token = CT(WhitespaceToken, LineNumberToken, WhitespaceToken,
                       InstructionNameToken, OT(CT(WhitespaceToken, arguments_token, OT(NewlineToken))))

from shader_source import ps_instruction_str as instruction_str

remaining = instruction_str
while remaining:
    try:
        tokens, remaining = instruction_token.eat(remaining)
        #print(list_str(tokens))
    except DXBCError as e:
        current_instruction_line = remaining[:remaining.index("\n")]
        reraise(e, f"{{}} encountered when tokenizing {current_instruction_line}, tokenized {instruction_str[:-len(remaining)]}")
        break

    try:
        instr_name, args_exprs = extract_instruction_data(tokens)
        instr = getInstructionType(instr_name)(instr_name, args_exprs)
    except ValueError as e:
        reraise(e, "{} encountered when disassembling " + list_str(tokens))
    print(instr.disassemble())
