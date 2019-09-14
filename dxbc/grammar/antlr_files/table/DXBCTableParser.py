# Generated from C:/Users/Samuel/PycharmProjects/DXBCDisassembler/dxbc/grammar/antlr_files/table\DXBCTable.g4 by ANTLR 4.7.2
# encoding: utf-8
from antlr4 import *
from io import StringIO
from typing.io import TextIO
import sys


def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3\7")
        buf.write("\34\4\2\t\2\4\3\t\3\3\2\7\2\b\n\2\f\2\16\2\13\13\2\3\2")
        buf.write("\3\2\6\2\17\n\2\r\2\16\2\20\6\2\23\n\2\r\2\16\2\24\3\3")
        buf.write("\6\3\30\n\3\r\3\16\3\31\3\3\2\2\4\2\4\2\2\2\35\2\t\3\2")
        buf.write("\2\2\4\27\3\2\2\2\6\b\7\5\2\2\7\6\3\2\2\2\b\13\3\2\2\2")
        buf.write("\t\7\3\2\2\2\t\n\3\2\2\2\n\22\3\2\2\2\13\t\3\2\2\2\f\16")
        buf.write("\5\4\3\2\r\17\7\5\2\2\16\r\3\2\2\2\17\20\3\2\2\2\20\16")
        buf.write("\3\2\2\2\20\21\3\2\2\2\21\23\3\2\2\2\22\f\3\2\2\2\23\24")
        buf.write("\3\2\2\2\24\22\3\2\2\2\24\25\3\2\2\2\25\3\3\2\2\2\26\30")
        buf.write("\7\6\2\2\27\26\3\2\2\2\30\31\3\2\2\2\31\27\3\2\2\2\31")
        buf.write("\32\3\2\2\2\32\5\3\2\2\2\6\t\20\24\31")
        return buf.getvalue()


class DXBCTableParser ( Parser ):

    grammarFileName = "DXBCTable.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'//'", "<INVALID>", "'\n'" ]

    symbolicNames = [ "<INVALID>", "COMMENT_START", "WS", "NEWLINE", "ID", 
                      "SEP" ]

    RULE_table = 0
    RULE_table_row = 1

    ruleNames =  [ "table", "table_row" ]

    EOF = Token.EOF
    COMMENT_START=1
    WS=2
    NEWLINE=3
    ID=4
    SEP=5

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.7.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class TableContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(DXBCTableParser.NEWLINE)
            else:
                return self.getToken(DXBCTableParser.NEWLINE, i)

        def table_row(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(DXBCTableParser.Table_rowContext)
            else:
                return self.getTypedRuleContext(DXBCTableParser.Table_rowContext,i)


        def getRuleIndex(self):
            return DXBCTableParser.RULE_table

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTable" ):
                listener.enterTable(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTable" ):
                listener.exitTable(self)




    def table(self):

        localctx = DXBCTableParser.TableContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_table)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 7
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==DXBCTableParser.NEWLINE:
                self.state = 4
                self.match(DXBCTableParser.NEWLINE)
                self.state = 9
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 16 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 10
                self.table_row()
                self.state = 12 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 11
                    self.match(DXBCTableParser.NEWLINE)
                    self.state = 14 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==DXBCTableParser.NEWLINE):
                        break

                self.state = 18 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==DXBCTableParser.ID):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Table_rowContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ID(self, i:int=None):
            if i is None:
                return self.getTokens(DXBCTableParser.ID)
            else:
                return self.getToken(DXBCTableParser.ID, i)

        def getRuleIndex(self):
            return DXBCTableParser.RULE_table_row

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTable_row" ):
                listener.enterTable_row(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTable_row" ):
                listener.exitTable_row(self)




    def table_row(self):

        localctx = DXBCTableParser.Table_rowContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_table_row)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 21 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 20
                self.match(DXBCTableParser.ID)
                self.state = 23 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==DXBCTableParser.ID):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





