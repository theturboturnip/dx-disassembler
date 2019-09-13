from dxbc.legacy.tokens.Base import RegexToken, Token

closers = {
    '(': ')',
    '[': ']',
    '{': '}',
}
openers = {
    ')': '(',
    ']': '[',
    '}': '{',
}


class ExpressionToken:
    def __init__(self, expr_type):
        self.expr_type = expr_type

    def eat(self, str_data):
        indent_stack = []
        i = 0
        while True:
            if i >= len(str_data):
                break
            c = str_data[i]
            if c == '\n':
                break
            #print("{}: {} stack = {}".format(i, c, indent_stack))
            if indent_stack == [] and c == ',':
                break
            if c in closers.keys():
                indent_stack.append(c)
            elif c in closers.values():
                if indent_stack[-1] != openers[c]:
                    raise ValueError("Mismatched paren: {} tried to close {}".format(c, openers[c]))
                indent_stack.pop()

            i += 1
        if indent_stack:
            raise ValueError("Unresolved indent stack at End of Expression {}".format(indent_stack))
        expr_str = str_data[0:i]
        expr = self.expr_type.create(expr_str)
        #print("Found expr str {}, made {}".format(expr_str, expr))
        return [ExpressionToken_Impl(expr_str, expr)], str_data[i:]


class ExpressionToken_Impl(Token, ExpressionToken):
    def __init__(self, str_data, expr):
        Token.__init__(self, str_data)
        #print ("ExpressionToken_Impl {}".format(expr))
        self.expr = expr

    def __str__(self):
        return "{}<{}>".format(super().__str__(), type(self.expr).__name__)


LineNumberToken = RegexToken(r"^(\d+):", "LineNumberToken")

InstructionNameToken = RegexToken(r"[^\s]+", "InstructionNameToken")