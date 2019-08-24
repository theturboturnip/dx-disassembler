from dxbc.tokens import *
from dxbc.v2.Base import Value, Untyped
from dxbc.v2.Scalar import *
from dxbc.v2.VarNames import *
from dxbc.v2.Vector import *

NegateToken = RegexToken("-", "NegateToken")
HexPrefixToken = RegexToken("0x", "HexPrefixToken")
HexDigitsToken = RegexToken(r"[\da-fA-F]+", "HexDigitsToken")
NumberToken = RegexToken(r"\d+", "NumberToken")
DotToken = RegexToken(r"\.", "DotToken")


class ValueHoldingToken:
    pass


class ImmediateScalarValueToken(
    ValueHoldingToken,
    SequenceToken(
        OptionalToken(NegateToken),
        FirstOfTokens(
            CompoundToken(HexPrefixToken, HexDigitsToken),
            CompoundToken(NumberToken, OptionalToken(DotToken), OptionalToken(NumberToken))
        )
    )
):
    def __init__(self, token_list):
        super().__init__(token_list)
        negated = False
        if isinstance(token_list[0], NegateToken):
            negated = True
            token_list = token_list[1:]
        value_type = int
        if len(token_list) > 1:
            # Either the HexToken is here, or the DotToken is
            if isinstance(token_list[0], HexPrefixToken):
                value_type = hex
                token_list = token_list[1:]
            else:
                value_type = float
        numerator_tok = token_list[0]
        denominator_tok = None
        if len(token_list) == 3:
            denominator_tok = token_list[2]

        if value_type == hex:
            value = int(numerator_tok.str_data, 16)
            value_type = int
        elif value_type == int:
            value = int(numerator_tok.str_data)
        elif value_type == float:
            value = float(f"{numerator_tok.str_data}.{denominator_tok.str_data}")
        else:
            raise DXBCTokenizeError("Invalid value_type detected: {}".format(value_type))
        self.value = ImmediateScalar(value, value_type, negated)


BaseNameToken = RegexToken(r"[\w_]+", "BaseNameToken")
ComponentToken = RegexToken(r"[xyzw]", "ComponentToken")
SwizzleToken = CompoundToken(RegexToken(r"\.", "DotToken"),
                             RepeatingToken(ComponentToken, min_repeats=1, max_repeats=4))


# TODO: Only correctly handles Scalars/Swizzled Vectors, not Unnamed vectors. Should prob be renamed.
def value_from_tokens(name: VarNameBase, component_tokens: List[ComponentToken], negated: bool) -> Value:
    if len(component_tokens) == 0:
        return ScalarVariable(name, Untyped, negated)
    elif len(component_tokens) == 1:
        return SingleVectorComponent(name, VectorComponent[component_tokens[0].str_data], Untyped, negated)
    else:
        return VectorValue(
            [SingleVectorComponent(name, VectorComponent[c.str_data], Untyped, False) for c in component_tokens],
            negated)


class SwizzledBasicNamedValueToken(
    ValueHoldingToken,
    SequenceToken(OptionalToken(NegateToken), BaseNameToken, OptionalToken(SwizzleToken))
):

    def __init__(self, token_list: List[Token]):
        super().__init__(token_list)
        negated = False
        if isinstance(token_list[0], NegateToken):
            negated = True
            token_list = token_list[1:]
        self.value = value_from_tokens(VarNameBase(token_list[0].str_data),
                                       list(filter(lambda x: isinstance(x, ComponentToken), token_list)),
                                       negated)


BasicNamedOrImmediateValueTokenTypes = (ImmediateScalarValueToken, SwizzledBasicNamedValueToken)
BasicNamedOrImmediateValueToken = FirstOfTokens(*BasicNamedOrImmediateValueTokenTypes)

IndexStartToken = RegexToken(r"\[", "IndexStartToken")
IndexEndToken = RegexToken(r"\]", "IndexEndToken")
IndexSeparatorToken = CompoundToken(WhitespaceToken,
                                    OptionalToken(RegexToken(r"\+", "AdditionToken")),
                                    OptionalToken(WhitespaceToken))


class SwizzledIndexedValueToken(
    ValueHoldingToken,
    SequenceToken(
        OptionalToken(NegateToken),
        BaseNameToken,
        IndexStartToken,
        BasicNamedOrImmediateValueToken,
        RepeatingToken(CompoundToken(IndexSeparatorToken, BasicNamedOrImmediateValueToken)),
        IndexEndToken,
        OptionalToken(SwizzleToken)
    )
):

    def __init__(self, token_list: List[Token]):
        super().__init__(token_list)
        negated = False
        if isinstance(token_list[0], NegateToken):
            negated = True
            token_list = token_list[1:]

        indices = [x.value for x in filter(lambda x: isinstance(x, NamedOrImmediateValueTokenTypes), token_list)]
        self.value = value_from_tokens(IndexedVarName(token_list[0].str_data, indices),
                                       list(filter(lambda x: isinstance(x, ComponentToken), token_list)),
                                       negated)


UnnamedVectorStartToken = RegexToken(r"\(", "UnnamedVectorStartToken")
UnnamedVectorEndToken = RegexToken(r"\)", "UnnamedVectorEndToken")
VectorValueSeparatorToken = CompoundToken(OptionalToken(WhitespaceToken),
                                          RegexToken(r",", "CommaToken"),
                                          OptionalToken(WhitespaceToken))

NamedOrImmediateValueTokenTypes = (ImmediateScalarValueToken, SwizzledIndexedValueToken, SwizzledBasicNamedValueToken)
NamedOrImmediateValueToken = FirstOfTokens(*NamedOrImmediateValueTokenTypes)


class UnnamedVectorValueToken(
    ValueHoldingToken,
    SequenceToken(
        OptionalToken(NegateToken),
        UnnamedVectorStartToken,
        NamedOrImmediateValueToken,
        RepeatingToken(CompoundToken(VectorValueSeparatorToken, NamedOrImmediateValueToken)),
        UnnamedVectorEndToken
    )
):
    def __init__(self, token_list):
        super().__init__(token_list)
        negated = False
        if isinstance(token_list[0], NegateToken):
            negated = True
            token_list = token_list[1:]

        token_list = token_list[1:-1] # Cut off UnnamedVectorStart/End tokens
        self.value = UnnamedVectorValue(
            [x.value for x in filter(lambda x: isinstance(x, NamedOrImmediateValueTokenTypes), token_list)],
            negated
        )


ValueToken = FirstOfTokens(UnnamedVectorValueToken, SwizzledIndexedValueToken, SwizzledBasicNamedValueToken,
                           ImmediateScalarValueToken)
