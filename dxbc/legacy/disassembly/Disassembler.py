from collections import Mapping

from dxbc.legacy.disassembly.Tokenizer import *
from dxbc.legacy.tokens import *
from dxbc.v2.program.program import Program
from dxbc.v2.program.program_generator import ProgramGenerator
from dxbc.v2.program.functions import *
from dxbc.v2.program.variables import *
from utils import *

class Disassembler:
    program: Program

    def __init__(self):
        self.tokenizer = Tokenizer()
        self.instructions = []

    def disassemble_file(self, file_contents: str):
        tokens, remaining = self.tokenizer.tokenize_file(file_contents)
        tokens = [x for x in tokens if not isinstance(x, (WhitespaceToken, NewlineToken))]
        if len(tokens) == 0 or not isinstance(tokens[0], SHADER_START_TOKEN):
            raise DXBCError("Expected SHADER_START_TOKEN at the beginning of the file")

        declaration_tokens = [x for x in tokens if isinstance(x, DECLARATION_TOKEN)]
        declaration_pairs: List[Tuple[DeclName, List[Value]]] = \
            [
                (
                    name_token_from_type(type(x.tokens[1])),
                    [t.value for t in x.tokens[3].tokens if hasattr(t, "value")]
                )
                for x in declaration_tokens
            ]
        decl_data: Mapping[DeclName, List[List[Value]]] = \
            {
                e: [x for x_e, x in declaration_pairs if x_e == e]
                for e in DeclName
            }

        instr_data = [
            self.tokenizer.extract_instruction_data(instr_tokens)
            for instr_tokens in [x.tokens for x in tokens if isinstance(x, INSTRUCTION_TOKEN)]
        ]

        self.program = ProgramGenerator().build_program(decl_data, instr_data)





