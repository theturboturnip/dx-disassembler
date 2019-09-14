# Generated from C:/Users/Samuel/PycharmProjects/DXBCDisassembler/dxbc/grammar/antlr_files/table\DXBCTable.g4 by ANTLR 4.7.2
from antlr4 import *
from io import StringIO
from typing.io import TextIO
import sys



def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\2\7")
        buf.write("\'\b\1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\3\2\3\2")
        buf.write("\3\2\3\2\3\2\3\3\6\3\24\n\3\r\3\16\3\25\3\3\3\3\3\4\3")
        buf.write("\4\3\5\6\5\35\n\5\r\5\16\5\36\3\6\6\6\"\n\6\r\6\16\6#")
        buf.write("\3\6\3\6\2\2\7\3\3\5\4\7\5\t\6\13\7\3\2\4\5\2\13\13\17")
        buf.write("\17\"\"\6\2\61;C\\aac|\2)\2\3\3\2\2\2\2\5\3\2\2\2\2\7")
        buf.write("\3\2\2\2\2\t\3\2\2\2\2\13\3\2\2\2\3\r\3\2\2\2\5\23\3\2")
        buf.write("\2\2\7\31\3\2\2\2\t\34\3\2\2\2\13!\3\2\2\2\r\16\7\61\2")
        buf.write("\2\16\17\7\61\2\2\17\20\3\2\2\2\20\21\b\2\2\2\21\4\3\2")
        buf.write("\2\2\22\24\t\2\2\2\23\22\3\2\2\2\24\25\3\2\2\2\25\23\3")
        buf.write("\2\2\2\25\26\3\2\2\2\26\27\3\2\2\2\27\30\b\3\2\2\30\6")
        buf.write("\3\2\2\2\31\32\7\f\2\2\32\b\3\2\2\2\33\35\t\3\2\2\34\33")
        buf.write("\3\2\2\2\35\36\3\2\2\2\36\34\3\2\2\2\36\37\3\2\2\2\37")
        buf.write("\n\3\2\2\2 \"\7/\2\2! \3\2\2\2\"#\3\2\2\2#!\3\2\2\2#$")
        buf.write("\3\2\2\2$%\3\2\2\2%&\b\6\2\2&\f\3\2\2\2\6\2\25\36#\3\b")
        buf.write("\2\2")
        return buf.getvalue()


class DXBCTableLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    COMMENT_START = 1
    WS = 2
    NEWLINE = 3
    ID = 4
    SEP = 5

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ "DEFAULT_MODE" ]

    literalNames = [ "<INVALID>",
            "'//'", "'\n'" ]

    symbolicNames = [ "<INVALID>",
            "COMMENT_START", "WS", "NEWLINE", "ID", "SEP" ]

    ruleNames = [ "COMMENT_START", "WS", "NEWLINE", "ID", "SEP" ]

    grammarFileName = "DXBCTable.g4"

    def __init__(self, input=None, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.7.2")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


