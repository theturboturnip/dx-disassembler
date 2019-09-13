import collections
from collections import Mapping
from itertools import chain

from dxbc.v2.disassembly.ProgramGenerator import Program, ProgramGenerator
from dxbc.v2.program.Functions import *
from dxbc.v2.program.State import ProgramState
from dxbc.v2.disassembly.Tokenizer import Tokenizer, INSTRUCTION_TOKEN, NewlineToken, WhitespaceToken, \
    SHADER_START_TOKEN, DECLARATION_TOKEN, NameToken, Token
from dxbc.v2.program.Variables import *
from dxbc.v2.values.tokens import ValueToken
from utils import *

# Any time an array access is made, all components are assumed to be of the mapped type
"""vector_constants = {
    "cb5": ScalarType.Float,
    "cb6": ScalarType.Float,
    "cb7": ScalarType.Float,
    "cb12": ScalarType.Float,
    "cb13": ScalarType.Float,

    "icb": ScalarType.Float,

    "v0": ScalarType.Float,
    "v1": ScalarType.Float,
    "v2": ScalarType.Float,
    "v3": ScalarType.Float,
    "v4": ScalarType.Float,
    "vCoverageMask": ScalarType.Uint,
    "values": ScalarType.Float,

    "t0": ScalarType.Untyped,
    "t1": ScalarType.Untyped,
    "t2": ScalarType.Untyped,

    "o0": ScalarType.Float,
    "o1": ScalarType.Float,
    "o2": ScalarType.Float,
    "o3": ScalarType.Float,
}
scalar_values = {
    "oMask": ScalarType.Uint
}
initial_scalar_types = {
    ScalarID(VarNameBase(name), comp): VariableState(None, t)
    for comp in VectorComponent
    for (name, t) in vector_constants.items()
}
initial_scalar_types.update({
    ScalarID(VarNameBase(name)): VariableState(None, t)
    for (name, t) in scalar_values.items()
})
initial_scalar_types.update({
    ScalarID(VarNameBase(name)): VariableState(None, ScalarType.Untyped)
    for name in [
        "s0", "s1", "s2",
    ]
})
initial_vec_state = {
    VarNameBase(name): 4
    for name, scalar_type in vector_constants.items()
    if scalar_type == ScalarType.Float
}
registers = [f"r{i}" for i in range(0, 7)]"""



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
        declaration_pairs: List[Tuple[NameToken, List[Value]]] = \
            [
                (
                    NameToken.from_type(type(x.tokens[1])),
                    [t.value for t in x.tokens[3].tokens if hasattr(t, "value")]
                )
                for x in declaration_tokens
            ]
        decl_data: Mapping[NameToken, List[List[Value]]] = \
            {
                e: [x for x_e, x in declaration_pairs if x_e == e]
                for e in NameToken
            }

        instr_data = [
            self.tokenizer.extract_instruction_data(instr_tokens)
            for instr_tokens in [x.tokens for x in tokens if isinstance(x, INSTRUCTION_TOKEN)]
        ]

        self.program = ProgramGenerator().build_program(decl_data, instr_data)





