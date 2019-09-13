from typing import Dict, List, Tuple, Sequence, Mapping

from dxbc.v2.disassembly.Tokenizer import NameToken
from dxbc.v2.values import Value


class ProgramGenerator:
    def __init__(self):
        pass

    def generate_program(self, decl_data: Mapping[NameToken, List[List[Value]]], instr_data: Sequence[Tuple[str, List[Value]]]):