# Generated from C:/Users/Samuel/PycharmProjects/DXBCDisassembler/dxbc/grammar/antlr_files\DXBC.g4 by ANTLR 4.7.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .DXBCParser import DXBCParser
else:
    from DXBCParser import DXBCParser

# This class defines a complete listener for a parse tree produced by DXBCParser.
class DXBCListener(ParseTreeListener):

    # Enter a parse tree produced by DXBCParser#dxbc_file.
    def enterDxbc_file(self, ctx:DXBCParser.Dxbc_fileContext):
        pass

    # Exit a parse tree produced by DXBCParser#dxbc_file.
    def exitDxbc_file(self, ctx:DXBCParser.Dxbc_fileContext):
        pass


    # Enter a parse tree produced by DXBCParser#shader_name.
    def enterShader_name(self, ctx:DXBCParser.Shader_nameContext):
        pass

    # Exit a parse tree produced by DXBCParser#shader_name.
    def exitShader_name(self, ctx:DXBCParser.Shader_nameContext):
        pass


    # Enter a parse tree produced by DXBCParser#declarations.
    def enterDeclarations(self, ctx:DXBCParser.DeclarationsContext):
        pass

    # Exit a parse tree produced by DXBCParser#declarations.
    def exitDeclarations(self, ctx:DXBCParser.DeclarationsContext):
        pass


    # Enter a parse tree produced by DXBCParser#declaration.
    def enterDeclaration(self, ctx:DXBCParser.DeclarationContext):
        pass

    # Exit a parse tree produced by DXBCParser#declaration.
    def exitDeclaration(self, ctx:DXBCParser.DeclarationContext):
        pass


    # Enter a parse tree produced by DXBCParser#instructions.
    def enterInstructions(self, ctx:DXBCParser.InstructionsContext):
        pass

    # Exit a parse tree produced by DXBCParser#instructions.
    def exitInstructions(self, ctx:DXBCParser.InstructionsContext):
        pass


    # Enter a parse tree produced by DXBCParser#instruction.
    def enterInstruction(self, ctx:DXBCParser.InstructionContext):
        pass

    # Exit a parse tree produced by DXBCParser#instruction.
    def exitInstruction(self, ctx:DXBCParser.InstructionContext):
        pass


    # Enter a parse tree produced by DXBCParser#instruction_name.
    def enterInstruction_name(self, ctx:DXBCParser.Instruction_nameContext):
        pass

    # Exit a parse tree produced by DXBCParser#instruction_name.
    def exitInstruction_name(self, ctx:DXBCParser.Instruction_nameContext):
        pass


    # Enter a parse tree produced by DXBCParser#value.
    def enterValue(self, ctx:DXBCParser.ValueContext):
        pass

    # Exit a parse tree produced by DXBCParser#value.
    def exitValue(self, ctx:DXBCParser.ValueContext):
        pass


    # Enter a parse tree produced by DXBCParser#scalar_value.
    def enterScalar_value(self, ctx:DXBCParser.Scalar_valueContext):
        pass

    # Exit a parse tree produced by DXBCParser#scalar_value.
    def exitScalar_value(self, ctx:DXBCParser.Scalar_valueContext):
        pass


    # Enter a parse tree produced by DXBCParser#vector_value.
    def enterVector_value(self, ctx:DXBCParser.Vector_valueContext):
        pass

    # Exit a parse tree produced by DXBCParser#vector_value.
    def exitVector_value(self, ctx:DXBCParser.Vector_valueContext):
        pass


    # Enter a parse tree produced by DXBCParser#component_value.
    def enterComponent_value(self, ctx:DXBCParser.Component_valueContext):
        pass

    # Exit a parse tree produced by DXBCParser#component_value.
    def exitComponent_value(self, ctx:DXBCParser.Component_valueContext):
        pass


    # Enter a parse tree produced by DXBCParser#immediate_scalar.
    def enterImmediate_scalar(self, ctx:DXBCParser.Immediate_scalarContext):
        pass

    # Exit a parse tree produced by DXBCParser#immediate_scalar.
    def exitImmediate_scalar(self, ctx:DXBCParser.Immediate_scalarContext):
        pass


    # Enter a parse tree produced by DXBCParser#single_vector_component.
    def enterSingle_vector_component(self, ctx:DXBCParser.Single_vector_componentContext):
        pass

    # Exit a parse tree produced by DXBCParser#single_vector_component.
    def exitSingle_vector_component(self, ctx:DXBCParser.Single_vector_componentContext):
        pass


    # Enter a parse tree produced by DXBCParser#scalar_variable.
    def enterScalar_variable(self, ctx:DXBCParser.Scalar_variableContext):
        pass

    # Exit a parse tree produced by DXBCParser#scalar_variable.
    def exitScalar_variable(self, ctx:DXBCParser.Scalar_variableContext):
        pass


    # Enter a parse tree produced by DXBCParser#immediate_vector.
    def enterImmediate_vector(self, ctx:DXBCParser.Immediate_vectorContext):
        pass

    # Exit a parse tree produced by DXBCParser#immediate_vector.
    def exitImmediate_vector(self, ctx:DXBCParser.Immediate_vectorContext):
        pass


    # Enter a parse tree produced by DXBCParser#swizzled_vector_variable.
    def enterSwizzled_vector_variable(self, ctx:DXBCParser.Swizzled_vector_variableContext):
        pass

    # Exit a parse tree produced by DXBCParser#swizzled_vector_variable.
    def exitSwizzled_vector_variable(self, ctx:DXBCParser.Swizzled_vector_variableContext):
        pass


    # Enter a parse tree produced by DXBCParser#variable_name.
    def enterVariable_name(self, ctx:DXBCParser.Variable_nameContext):
        pass

    # Exit a parse tree produced by DXBCParser#variable_name.
    def exitVariable_name(self, ctx:DXBCParser.Variable_nameContext):
        pass


    # Enter a parse tree produced by DXBCParser#array_index.
    def enterArray_index(self, ctx:DXBCParser.Array_indexContext):
        pass

    # Exit a parse tree produced by DXBCParser#array_index.
    def exitArray_index(self, ctx:DXBCParser.Array_indexContext):
        pass


    # Enter a parse tree produced by DXBCParser#brace_list_or_val.
    def enterBrace_list_or_val(self, ctx:DXBCParser.Brace_list_or_valContext):
        pass

    # Exit a parse tree produced by DXBCParser#brace_list_or_val.
    def exitBrace_list_or_val(self, ctx:DXBCParser.Brace_list_or_valContext):
        pass


    # Enter a parse tree produced by DXBCParser#brace_list.
    def enterBrace_list(self, ctx:DXBCParser.Brace_listContext):
        pass

    # Exit a parse tree produced by DXBCParser#brace_list.
    def exitBrace_list(self, ctx:DXBCParser.Brace_listContext):
        pass


