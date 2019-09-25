import re
import typing
from typing import List, Optional, Mapping

from dxbc.Errors import DXBCError
from dxbc.v2.program.declarations import Declaration
from dxbc.v2.types import ScalarType

Semantic = typing.NamedTuple("Semantic", [("semantic_name", str), ("register", str), ("scalar_type", ScalarType), ("length", int)])

class SemanticSet:
    semantic = Mapping[str, Semantic]

    def __init__(self):
        self.semantics = {}
        self.append(Semantic("SV_COVERAGE", "vCoverage", ScalarType.Uint, 1))
        self.append(Semantic("SV_COVERAGE", "vCoverageMask", ScalarType.Uint, 1))
        self.append(Semantic("SV_COVERAGE", "oMask", ScalarType.Uint, 1))


    def append(self, new_sem: Semantic):
        self.semantics[new_sem.register] = new_sem

    def match_declaration(self, decl: Declaration) -> Semantic:
        decl_name_str = decl.value_list[0].get_var_name().as_base().name
        if decl_name_str in self.semantics:
            return self.semantics[decl_name_str]

        # If the declname is xN, we can match the semantic of index N
        match = re.match(r"[a-zA-Z](\d+)", decl_name_str)
        if not match:
            raise DXBCError(f"'{decl_name_str}' does not exactly match a string register and can't be reduced to a numeric register")

        if match.group(1) not in self.semantics:
            print(self.semantics)
            raise DXBCError(f"numeric register {match.group(1)} from '{decl_name_str}' not found in semantic set")

        return self.semantics[match.group(1)]