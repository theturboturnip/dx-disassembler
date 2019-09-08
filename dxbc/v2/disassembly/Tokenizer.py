from enum import Enum, IntEnum
from typing import cast

from dxbc.Errors import DXBCInstructionDecodeError, DXBCError
from dxbc.tokens import *
from dxbc.v2.values import Value
from dxbc.v2.values.tokens import ValueToken, ValueHoldingToken
from utils import reraise

CT = CompoundToken
OT = OptionalToken

ARGUMENTS_TOKEN = OT(CT(
    ValueToken,
    RepeatingToken(
        CT(RegexToken(",", "comma"), WhitespaceToken, ValueToken)
    )
))
INSTRUCTION_TOKEN = SequenceToken(
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

PS_SHADER_START_TOKEN = RegexToken("ps_\d_\d", "PS_SHADER_START_TOKEN")

SHADER_START_TOKEN = SequenceToken(FirstOfTokens(PS_SHADER_START_TOKEN))

GLOBAL_FLAGS_TOKEN = RegexToken(r"globalFlags")
IMMEDIATE_BUFFER_TOKEN = SequenceToken(
    RegexToken(r"immediateConstantBuffer"), WhitespaceToken, RegexToken(r"\{[\s\S]+? \}")
)
CONSTANT_BUFFER_TOKEN = RegexToken(r"constantbuffer")
SAMPLER_TOKEN = RegexToken(r"sampler")
TEXTURE_TOKEN = RegexToken(r"resource_texture2d \(float,float,float,float\)")
TYPED_PS_INPUT = SequenceToken(
    RegexToken(r"input_ps "), RegexToken(r"linearCentroid")
)
UNTYPED_INPUT = RegexToken(r"input(_ps_siv)?")
OUTPUT = RegexToken(r"output")
REGISTER_COUNT = RegexToken(r"temps")

class NameToken(IntEnum):
    GlobalFlags = 0,
    ImmediateBufferToken = 1,
    ConstantBufferToken = 2,
    SamplerToken = 3,
    TextureToken = 4,
    TypedPSInput = 5,
    UntypedInput = 6,
    Output = 7,
    RegisterCount = 8

    def to_type(self) -> Type[Token]:
        return NAME_TOKENS_TYPE_LIST[self.value]

    @staticmethod
    def from_type(t: Type[Token]) -> 'NameToken':
        return NameToken(NAME_TOKENS_TYPE_LIST.index(t))

NAME_TOKENS_TYPE_LIST = [
    GLOBAL_FLAGS_TOKEN,
    IMMEDIATE_BUFFER_TOKEN,
    CONSTANT_BUFFER_TOKEN,
    SAMPLER_TOKEN,
    TEXTURE_TOKEN,
    TYPED_PS_INPUT,
    UNTYPED_INPUT,
    OUTPUT,
    REGISTER_COUNT
]

DECLARATION_START_TOKEN = SequenceToken(WhitespaceToken, RegexToken("dcl_", "DeclToken"))
DECLARATION_NAME_TOKEN = FirstOfTokens(*NAME_TOKENS_TYPE_LIST)
DECLARATION_TOKEN = SequenceToken(
    DECLARATION_START_TOKEN,
    DECLARATION_NAME_TOKEN,
    RegexToken(r"[ ]*", "WhitespaceNoNewlineToken"),
    SequenceToken(ARGUMENTS_TOKEN),
    NewlineToken
)

def make_file_token(*token_types: Type[Token]):
    class CompoundToken_Impl(Token):
        @staticmethod
        def eat(str_data) -> EatReturnType:
            tokens = []
            remaining_data = str_data
            line_number = 0
            for token_type in token_types:
                try:
                    new_token_list, remaining_data = token_type.eat(remaining_data)
                    tokens += new_token_list
                except DXBCError as e:
                    current_instruction_line = remaining_data[:remaining_data.index("\n")]
                    reraise(e,
                            f"Error when tokenizing line {line_number} \"{current_instruction_line}\":\n\t{{}}, "
                            f"tokens so far: {tokens}".replace("{", "{{").replace("}", "}}"))
                    raise
                line_number += 1
            return tokens, remaining_data
    return CompoundToken_Impl

FILE_TOKEN = make_file_token(
    OT(WhitespaceToken),
    SHADER_START_TOKEN, NewlineToken,
    RepeatingToken(DECLARATION_TOKEN, 3),
    RepeatingToken(INSTRUCTION_TOKEN)
)

class Tokenizer:
    def tokenize_file(self, file_contents: str):
        remaining = file_contents
        try:
            tokens, remaining = FILE_TOKEN.eat(remaining)
        except DXBCError as e:
            reraise(e,
                    f"Error when tokenizing file:\n\t{{}}")
            raise
        return tokens, remaining

    """def next_instruction(self, remaining) -> Tuple[Tuple[str, List[Value]], str]:
        try:
            tokens, remaining = INSTRUCTION_TOKEN.eat(remaining)
        except DXBCError as e:
            current_instruction_line = remaining[:remaining.index("\n")]
            reraise(e,
                    f"{{}} encountered when tokenizing {current_instruction_line}, tokenized {remaining[:-len(remaining)]}")
            raise

        instruction_token: INSTRUCTION_TOKEN = cast(INSTRUCTION_TOKEN, tokens[0])

        try:
            return self.extract_instruction_data(instruction_token.tokens), remaining
        except DXBCError as e:
            reraise(e, "{} encountered when disassembling " + list_str(tokens))
            raise"""

    def extract_instruction_data(self, tokens: List[Token]) -> Tuple[str, List[Value]]:
        if not isinstance(tokens, list):
            tokens = list(tokens)
        instr_tokens = list(filter(lambda x: isinstance(x, InstructionNameToken), tokens))
        arg_tokens = list(filter(lambda x: isinstance(x, ValueHoldingToken), tokens))
        arg_vals = list(map(lambda x: x.value, arg_tokens))

        if len(instr_tokens) != 1:
            raise DXBCInstructionDecodeError("Expected 1 InstructionNameToken, got {}".format(len(instr_tokens)))

        return instr_tokens[0].str_data, arg_vals