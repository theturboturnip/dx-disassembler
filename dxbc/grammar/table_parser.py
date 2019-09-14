from typing import List

from antlr4 import *

from dxbc.Errors import DXBCError
from dxbc.grammar.antlr_files.table.DXBCTableLexer import DXBCTableLexer
from dxbc.grammar.antlr_files.table.DXBCTableListener import DXBCTableListener
from dxbc.grammar.antlr_files.table.DXBCTableParser import DXBCTableParser

numbered_semantics = {"TEXCOORD", "SV_TARGET"}

class SemanticTableParser(DXBCTableListener):
    semantic_strs: List[str]
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

        if self.table[0][:2] != ["Name", "Index"]:
            raise DXBCError("First columns were not Name and Index as expected")
        for row in self.table[1:]:
            name = row[0]
            if name in numbered_semantics:
                index = int(row[1])
                self.semantic_strs.append(f"{name}{index}")
            else:
                self.semantic_strs.append(name)

    def enterTable(self, ctx:DXBCTableParser.TableContext):
        self.table = [self.table_row_data(row) for row in ctx.table_row()]

    def table_row_data(self, ctx:DXBCTableParser.Table_rowContext) -> List[str]:
        return [item.getText() for item in ctx.ID()]