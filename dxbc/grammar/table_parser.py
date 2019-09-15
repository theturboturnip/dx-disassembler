import collections
import typing
from typing import List, Type, Tuple

from antlr4 import *

from dxbc.Errors import DXBCError
from dxbc.grammar.antlr_files.table.DXBCTableLexer import DXBCTableLexer
from dxbc.grammar.antlr_files.table.DXBCTableListener import DXBCTableListener
from dxbc.grammar.antlr_files.table.DXBCTableParser import DXBCTableParser
from dxbc.v2.types import ScalarType

numbered_semantics = {"TEXCOORD", "SV_TARGET"}

Semantic = typing.NamedTuple("Semantic", [("name", str), ("scalar_type", ScalarType), ("length", int)])

class SemanticTableParser(DXBCTableListener):
    semantic_strs: List[Semantic]
    table: List[List[str]]

    def __init__(self, table_data: str):
        input_stream = InputStream(table_data)
        lexer = DXBCTableLexer(input_stream)
        stream = CommonTokenStream(lexer)
        parser = DXBCTableParser(stream)
        tree = parser.table()

        walker = ParseTreeWalker()
        walker.walk(self, tree)

        self.semantic_strs = []

        if self.table[0][:6] != ["Name", "Index", "Mask", "Register", "SysValue", "Format"]:
            raise DXBCError("First columns were not Name and Index as expected")
        for row in self.table[1:]:
            name = row[0]
            scalar_type = ScalarType.from_name(row[5])
            vector_length = len(row[2]) if row[2] != "N/A" else 1

            full_name = name
            if name in numbered_semantics:
                index = int(row[1])
                full_name = f"{name}{index}"

            self.semantic_strs.append(Semantic(full_name, scalar_type, vector_length))

    def enterTable(self, ctx:DXBCTableParser.TableContext):
        self.table = [self.table_row_data(row) for row in ctx.table_row()]

    def table_row_data(self, ctx:DXBCTableParser.Table_rowContext) -> List[str]:
        return [item.getText() for item in ctx.ID()]