from dxbc.Errors import DXBCInstructionDecodeError, DXBCError
from dxbc.tokens import *
from dxbc.v2.values import Value
from dxbc.v2.values.tokens import ValueToken, ValueHoldingToken
from utils import reraise


class Tokenizer:
    CT = CompoundToken
    OT = OptionalToken

    ARGUMENTS_TOKEN = OT(CT(
        ValueToken,
        RepeatingToken(
            CT(RegexToken(",", "comma"), WhitespaceToken, ValueToken)
        )
    ))
    INSTRUCTION_TOKEN = CT(
        WhitespaceToken,
        LineNumberToken,
        WhitespaceToken,
        InstructionNameToken,
        OT(CT(
            WhitespaceToken,
            ARGUMENTS_TOKEN,
        )),
        OT(NewlineToken)
    )

    def next_instruction(self, remaining) -> Tuple[Tuple[str, List[Value]], str]:
        try:
            tokens, remaining = self.INSTRUCTION_TOKEN.eat(remaining)
        except DXBCError as e:
            current_instruction_line = remaining[:remaining.index("\n")]
            reraise(e,
                    f"{{}} encountered when tokenizing {current_instruction_line}, tokenized {remaining[:-len(remaining)]}")
            raise

        try:
            return self.extract_instruction_data(tokens), remaining
        except DXBCError as e:
            reraise(e, "{} encountered when disassembling " + list_str(tokens))
            raise

    def extract_instruction_data(self, tokens: List[Token]) -> Tuple[str, List[Value]]:
        if not isinstance(tokens, list):
            tokens = list(tokens)
        instr_tokens = list(filter(lambda x: isinstance(x, InstructionNameToken), tokens))
        arg_tokens = list(filter(lambda x: isinstance(x, ValueHoldingToken), tokens))
        arg_vals = list(map(lambda x: x.value, arg_tokens))

        if len(instr_tokens) != 1:
            raise DXBCInstructionDecodeError("Expected 1 InstructionNameToken, got {}".format(len(instr_tokens)))

        return instr_tokens[0].str_data, arg_vals