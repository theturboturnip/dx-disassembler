from antlr4 import *

from .antlr_files.DXBCListener import DXBCListener
from .antlr_files.DXBCLexer import DXBCLexer
from .antlr_files.DXBCParser import DXBCParser

class DisassemblyParser:
    class DataGather(DXBCListener):
        def enterDeclaration(self, ctx: DXBCParser.DeclarationContext):

            pass
        def exitDeclaration(self, ctx: DXBCParser.DeclarationContext):
            pass

        def enterInstruction(self, ctx: DXBCParser.InstructionContext):
            pass
        def exitInstruction(self, ctx: DXBCParser.InstructionContext):
            pass

    def __init__(self, str_data: str):
        input_stream = InputStream(str_data)
        lexer = DXBCLexer(input_stream)
        stream = CommonTokenStream(lexer)
        parser = DXBCParser(stream)
        tree = parser.dxbc_file()

        data_gather = self.DataGather()
        walker = ParseTreeWalker()
        walker.walk(data_gather, tree)