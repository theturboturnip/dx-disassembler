# Generated from C:/Users/Samuel/PycharmProjects/DXBCDisassembler/dxbc/grammar/antlr_files\DXBC.g4 by ANTLR 4.7.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .DXBCParser import DXBCParser
else:
    from DXBCParser import DXBCParser

# This class defines a complete generic visitor for a parse tree produced by DXBCParser.

class DXBCVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by DXBCParser#dxbc_file.
    def visitDxbc_file(self, ctx:DXBCParser.Dxbc_fileContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DXBCParser#shader_name.
    def visitShader_name(self, ctx:DXBCParser.Shader_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DXBCParser#declarations.
    def visitDeclarations(self, ctx:DXBCParser.DeclarationsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DXBCParser#declaration.
    def visitDeclaration(self, ctx:DXBCParser.DeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DXBCParser#instructions.
    def visitInstructions(self, ctx:DXBCParser.InstructionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DXBCParser#instruction.
    def visitInstruction(self, ctx:DXBCParser.InstructionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DXBCParser#instruction_name.
    def visitInstruction_name(self, ctx:DXBCParser.Instruction_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DXBCParser#value.
    def visitValue(self, ctx:DXBCParser.ValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DXBCParser#scalar_value.
    def visitScalar_value(self, ctx:DXBCParser.Scalar_valueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DXBCParser#vector_value.
    def visitVector_value(self, ctx:DXBCParser.Vector_valueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DXBCParser#component_value.
    def visitComponent_value(self, ctx:DXBCParser.Component_valueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DXBCParser#immediate_scalar.
    def visitImmediate_scalar(self, ctx:DXBCParser.Immediate_scalarContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DXBCParser#single_component.
    def visitSingle_component(self, ctx:DXBCParser.Single_componentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DXBCParser#swizzle_components.
    def visitSwizzle_components(self, ctx:DXBCParser.Swizzle_componentsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DXBCParser#single_vector_component.
    def visitSingle_vector_component(self, ctx:DXBCParser.Single_vector_componentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DXBCParser#scalar_variable.
    def visitScalar_variable(self, ctx:DXBCParser.Scalar_variableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DXBCParser#immediate_vector.
    def visitImmediate_vector(self, ctx:DXBCParser.Immediate_vectorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DXBCParser#swizzled_vector_variable.
    def visitSwizzled_vector_variable(self, ctx:DXBCParser.Swizzled_vector_variableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DXBCParser#variable_name.
    def visitVariable_name(self, ctx:DXBCParser.Variable_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DXBCParser#array_index.
    def visitArray_index(self, ctx:DXBCParser.Array_indexContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DXBCParser#brace_list_or_val.
    def visitBrace_list_or_val(self, ctx:DXBCParser.Brace_list_or_valContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DXBCParser#brace_list.
    def visitBrace_list(self, ctx:DXBCParser.Brace_listContext):
        return self.visitChildren(ctx)



del DXBCParser