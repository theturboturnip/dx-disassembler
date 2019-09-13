from dxbc.legacy.exprs import ValueExpr
from dxbc.legacy.tokens.BasicTokens import WhitespaceToken
from dxbc.legacy.tokens.Combinators import CompoundToken, OptionalToken, RepeatingToken
from utils import list_str

CT = CompoundToken
OT = OptionalToken

value_expr_token = ExpressionToken(ValueExpr)

test_token = RepeatingToken(CT(RegexToken(r"\d+"), OT(CT(RegexToken(","), WhitespaceToken))))
print(", ".join([str(x) for x in test_token.eat("1,2,3,4,5,")[0]]))
print(list_str(test_token.eat("1, 2, 3, 4, 5")[0]))
print(list_str(value_expr_token.eat("r0.y")[0]))