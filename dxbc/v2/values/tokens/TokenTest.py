import unittest
from itertools import permutations
from numbers import Number

from dxbc.v2.values import *
from dxbc.v2.values.tokens import *


class ImmediateScalarValueTokenTestCase(unittest.TestCase):
    def test_whitespace_throws(self):
        with self.assertRaises(DXBCTokenizeError):
            SwizzledBasicNamedValueToken.eat("")
        with self.assertRaises(DXBCTokenizeError):
            SwizzledBasicNamedValueToken.eat(" ")
        with self.assertRaises(DXBCTokenizeError):
            SwizzledBasicNamedValueToken.eat("\n")

    def valid_test(self, data, expected_value):
        try:
            token_list, remaining = ImmediateScalarValueToken.eat(data)
            self.assertEqual(len(token_list), 1)
            self.assertIsInstance(token_list[0], ImmediateScalarValueToken)
            self.assertFalse(remaining)
            self.assertEqual(token_list[0].value, expected_value)
        except (DXBCTokenizeError, AssertionError) as e:
            print("error while tokenizing {}".format(data))
            raise e

    def test_valid_ints(self):
        for i in range(-10000, 10000):
            self.valid_test(str(i), ImmediateScalar(abs(i), ScalarType.Int, i < 0))

    def test_valid_hex(self):
        for i in range(-10000, 10000):
            self.valid_test(hex(i), ImmediateScalar(abs(i), ScalarType.Hex, i < 0))

    def test_valid_float(self):
        i = -1000.0
        while i <= 1000.0:
            self.valid_test(f"{i:.32f}", ImmediateScalar(abs(i), ScalarType.Float, i < 0))
            i += 0.1

    def test_letters(self):
        with self.assertRaises(DXBCTokenizeError):
            ImmediateScalarValueToken.eat("abc")


class BasicNamedValueTokenTestCase(unittest.TestCase):
    def test_whitespace_throws(self):
        with self.assertRaises(DXBCTokenizeError):
            SwizzledBasicNamedValueToken.eat("")
        with self.assertRaises(DXBCTokenizeError):
            SwizzledBasicNamedValueToken.eat(" ")
        with self.assertRaises(DXBCTokenizeError):
            SwizzledBasicNamedValueToken.eat("\n")

    def test_bad_swizzle(self):
        with self.assertRaises(DXBCTokenizeError):
            SwizzledBasicNamedValueToken.eat(".")

    def valid_test(self, data, expected_value):
        try:
            token_list, remaining = SwizzledBasicNamedValueToken.eat(data)
            self.assertEqual(len(token_list), 1)
            self.assertIsInstance(token_list[0], SwizzledBasicNamedValueToken)
            self.assertFalse(remaining)
            self.assertEqual(expected_value, token_list[0].value)
        except (DXBCTokenizeError, AssertionError) as e:
            print("error while tokenizing {}".format(data))
            raise e

    def test_valid_values(self):
        def test_scalar_variable(name):
            for negated in [True, False]:
                self.valid_test("{}{}".format("-" if negated else "", name),
                                ScalarVariable(VarNameBase(name), ScalarType.Untyped, negated))
        test_scalar_variable("x")
        test_scalar_variable("name_with_underscore")
        test_scalar_variable("name_with_number1")

        def test_scalar_component(vector_name: str, component: str):
            for negated in [True, False]:
                self.valid_test(
                    "{}{}.{}".format("-" if negated else "", vector_name, component),
                    SingleVectorComponent(VarNameBase(vector_name), VectorComponent[component], ScalarType.Untyped, negated)
                )
        test_scalar_component("var", "x")
        test_scalar_component("var", "y")
        test_scalar_component("var", "z")
        test_scalar_component("var", "w")

        def test_swizzled_vector(vector_name: str, *components: List[VectorComponent]):
            for negated in [True, False]:
                for perm in permutations(components):
                    self.valid_test(
                        "{}{}.{}".format("-" if negated else "", vector_name, "".join([x.name for x in perm[0]])),
                        SwizzledVectorValue(
                            [SingleVectorComponent(VarNameBase(vector_name), x, ScalarType.Untyped, False) for x in perm[0]],
                            negated
                        )
                    )

        test_swizzled_vector("var", [VectorComponent.x, VectorComponent.y])
        test_swizzled_vector("var", [VectorComponent.x, VectorComponent.y, VectorComponent.z])
        test_swizzled_vector("var", [VectorComponent.x, VectorComponent.y, VectorComponent.z, VectorComponent.w])


class SubscriptedNamedValueTokenTestCase(unittest.TestCase):
    def test_whitespace_throws(self):
        with self.assertRaises(DXBCTokenizeError):
            SwizzledIndexedValueToken.eat("")
        with self.assertRaises(DXBCTokenizeError):
            SwizzledIndexedValueToken.eat(" ")
        with self.assertRaises(DXBCTokenizeError):
            SwizzledIndexedValueToken.eat("\n")

    def test_no_index(self):
        with self.assertRaises(DXBCTokenizeError):
            SwizzledIndexedValueToken.eat("var[]")

    def valid_test(self, data, expected_value):
        try:
            token_list, remaining = SwizzledIndexedValueToken.eat(data)
            self.assertEqual(len(token_list), 1)
            self.assertIsInstance(token_list[0], SwizzledIndexedValueToken)
            self.assertFalse(remaining)
            self.assertEqual(expected_value, token_list[0].value)
        except (DXBCTokenizeError, AssertionError) as e:
            print("error while tokenizing {}".format(data))
            raise e

    def subscript_valid_scalar_test(self, name, subscripts: List[ScalarValueBase]):
        for negated in [True, False]:
            self.valid_test("{}{}[{}]".format("-" if negated else "", name, " + ".join(str(s) for s in subscripts)),
                            ScalarVariable(IndexedVarName(name, subscripts), ScalarType.Untyped, negated))

    def subscript_valid_vector_test(self, vector_name, subscripts: List[ScalarValueBase], components):
        for negated in [True, False]:
            self.valid_test(
                "{}{}[{}].{}".format(
                    "-" if negated else "", vector_name,
                    " + ".join(str(s) for s in subscripts),
                    "".join(x.name for x in components)
                ),
                SwizzledVectorValue(
                    [SingleVectorComponent(
                        IndexedVarName(vector_name, subscripts)
                        , x, ScalarType.Untyped, False
                    ) for x in components],
                    negated
                )
            )

    def subscript_single_component_test(self, vector_name: str, subscripts: List[ScalarValueBase], component: VectorComponent):
        for negated in [True, False]:
            self.valid_test(
                "{}{}[{}].{}".format("-" if negated else "", vector_name, " + ".join(str(s) for s in subscripts), component.name),
                SingleVectorComponent(IndexedVarName(vector_name, subscripts), component, ScalarType.Untyped, negated)
            )

    def test_variable_subscript(self):
        subscripts = [SingleVectorComponent(VarNameBase("var"), VectorComponent.x, ScalarType.Untyped, False)]
        self.subscript_valid_scalar_test("x", subscripts)
        self.subscript_valid_scalar_test("name_with_underscore", subscripts)
        self.subscript_valid_scalar_test("name_with_number1", subscripts)

    def test_complex_subscripts(self):
        subscripts = [
            SingleVectorComponent(VarNameBase("var"), VectorComponent.x, ScalarType.Untyped, False),
            SingleVectorComponent(VarNameBase("alpha"), VectorComponent.z, ScalarType.Untyped, True),
            ImmediateScalar(1, ScalarType.Int, False),
            SingleVectorComponent(VarNameBase("beta"), VectorComponent.y, ScalarType.Untyped, False)
        ]
        self.subscript_valid_scalar_test("x", subscripts)
        self.subscript_valid_scalar_test("name_with_underscore", subscripts)
        self.subscript_valid_scalar_test("name_with_number1", subscripts)
        self.subscript_single_component_test("var", subscripts, VectorComponent.x)
        self.subscript_single_component_test("var", subscripts, VectorComponent.y)
        self.subscript_single_component_test("var", subscripts, VectorComponent.z)
        self.subscript_single_component_test("var", subscripts, VectorComponent.w)

        def test_swizzled_vector(vector_name: str, subscripts: List[ScalarValueBase], components: List[VectorComponent]):
            for perm in permutations(components):
                self.subscript_valid_vector_test(vector_name, subscripts, perm)

        test_swizzled_vector("var", subscripts, [VectorComponent.x, VectorComponent.y])
        test_swizzled_vector("var", subscripts, [VectorComponent.x, VectorComponent.y, VectorComponent.z])
        test_swizzled_vector("var", subscripts, [VectorComponent.x, VectorComponent.y, VectorComponent.z, VectorComponent.w])
        test_swizzled_vector("var", subscripts, [VectorComponent.w, VectorComponent.y, VectorComponent.z])

    def test_scalar_array(self):
        subscripts = [ImmediateScalar(0, ScalarType.Int, False)]
        self.subscript_valid_scalar_test("x", subscripts)
        self.subscript_valid_scalar_test("name_with_underscore", subscripts)
        self.subscript_valid_scalar_test("name_with_number1", subscripts)

    def test_vector_array(self):
        zero = ImmediateScalar(0, ScalarType.Int, False)

        self.subscript_single_component_test("var", [zero], VectorComponent.x)
        self.subscript_single_component_test("var", [zero], VectorComponent.y)
        self.subscript_single_component_test("var", [zero], VectorComponent.z)
        self.subscript_single_component_test("var", [zero], VectorComponent.w)

        def test_swizzled_vector(vector_name: str, subscript: ScalarValueBase, components: List[VectorComponent]):
            for perm in permutations(components):
                self.subscript_valid_vector_test(vector_name, [subscript], perm)

        test_swizzled_vector("var", zero, [VectorComponent.x, VectorComponent.y])
        test_swizzled_vector("var", zero, [VectorComponent.x, VectorComponent.y, VectorComponent.z])
        test_swizzled_vector("var", zero, [VectorComponent.x, VectorComponent.y, VectorComponent.z, VectorComponent.w])
        test_swizzled_vector("var", zero,                    [VectorComponent.w, VectorComponent.y, VectorComponent.z])


class UnnamedVectorValueTokenTestCase(unittest.TestCase):
    def test_whitespace_throws(self):
        with self.assertRaises(DXBCTokenizeError):
            UnnamedVectorValueToken.eat("")
        with self.assertRaises(DXBCTokenizeError):
            UnnamedVectorValueToken.eat(" ")
        with self.assertRaises(DXBCTokenizeError):
            UnnamedVectorValueToken.eat("\n")

    def test_empty(self):
        with self.assertRaises(DXBCTokenizeError):
            UnnamedVectorValueToken.eat("()")

    def test_no_sep(self):
        with self.assertRaises(DXBCTokenizeError):
            tokens, rem = UnnamedVectorValueToken.eat("(1 2)")
            print(tokens[0].value)

    def valid_test(self, data, expected_value):
        try:
            token_list, remaining = UnnamedVectorValueToken.eat(data)
            self.assertEqual(len(token_list), 1)
            self.assertIsInstance(token_list[0], UnnamedVectorValueToken)
            self.assertFalse(remaining)
            self.assertEqual(expected_value, token_list[0].value)
        except (DXBCTokenizeError, AssertionError) as e:
            print("error while tokenizing {}".format(data))
            raise e

    def test_literals(self):
        def test_number_combo(*numbers: Number):
            scalar_list = [ImmediateScalar(abs(i), ScalarType.enum_from_type(type(i)), i < 0) for i in numbers]
            for negated in [True, False]:
                self.valid_test(
                    "{}({})".format("-" if negated else "", ", ".join(str(i) for i in numbers)),
                    UnnamedVectorValue(scalar_list, negated)
                )
        test_number_combo(1, 2)
        test_number_combo(1, 2, 3)
        test_number_combo(1, 2, 3, 4)

        test_number_combo(1.0, 2, -56.0, 2.0/3)

    def test_variables(self):
        def test_number_combo(*vars: ScalarValueBase):
            scalar_list = list(vars)
            for negated in [True, False]:
                self.valid_test(
                    "{}({})".format("-" if negated else "", ", ".join(str(i) for i in vars)),
                    UnnamedVectorValue(scalar_list, negated)
                )
        test_number_combo(ScalarVariable(VarNameBase("x"), ScalarType.Untyped, False),
                          ScalarVariable(VarNameBase("y"), ScalarType.Untyped, True))
        test_number_combo(SingleVectorComponent(VarNameBase("vec"), VectorComponent.x, ScalarType.Untyped, False),
                          ScalarVariable(VarNameBase("y"), ScalarType.Untyped, True))
        test_number_combo(ScalarVariable(VarNameBase("x"), ScalarType.Untyped, False),
                          SingleVectorComponent(VarNameBase("vec"), VectorComponent.y, ScalarType.Untyped, True))
        test_number_combo(SingleVectorComponent(VarNameBase("vec"), VectorComponent.x, ScalarType.Untyped, False),
                          SingleVectorComponent(VarNameBase("vec"), VectorComponent.y, ScalarType.Untyped, True))

        test_number_combo(ScalarVariable(IndexedVarName("vals", [ImmediateScalar(0, ScalarType.Int, False)]), ScalarType.Untyped, False),
                          ScalarVariable(IndexedVarName("vals", [ImmediateScalar(1, ScalarType.Int, False)]), ScalarType.Untyped, True))


class ValueTokenTest(unittest.TestCase):
    def test_whitespace_throws(self):
        with self.assertRaises(DXBCTokenizeError):
            ValueToken.eat("")
        with self.assertRaises(DXBCTokenizeError):
            ValueToken.eat(" ")
        with self.assertRaises(DXBCTokenizeError):
            ValueToken.eat("\n")

    def test_empty(self):
        with self.assertRaises(DXBCTokenizeError):
            ValueToken.eat("()")

    def test_no_sep(self):
        with self.assertRaises(DXBCTokenizeError):
            tokens, rem = ValueToken.eat("(1 2)")
            print(tokens[0].value)

    def valid_test(self, data, expected_value):
        try:
            token_list, remaining = ValueToken.eat(data)
            self.assertEqual(len(token_list), 1)
            self.assertIsInstance(token_list[0], ValueToken)
            self.assertFalse(remaining)
            self.assertEqual(expected_value, token_list[0].value)
        except (DXBCTokenizeError, AssertionError) as e:
            print("error while tokenizing {}".format(data))
            raise e

    def test(self):
        long_index = IndexedVarName("constants", [
            ImmediateScalar(255, ScalarType.Int, False),
            ImmediateScalar(1, ScalarType.Int, True),
            ImmediateScalar(3, ScalarType.Float, False),
            SingleVectorComponent(VarNameBase("vec"), VectorComponent.x, ScalarType.Untyped, True)
        ])
        tests = {
            "1": ImmediateScalar(1, ScalarType.Int, False),
            "0xFF": ImmediateScalar(255, ScalarType.Int, False),
            "-(1, -2.0, 3.0, -4)": UnnamedVectorValue([
                ImmediateScalar(1, ScalarType.Int, False),
                ImmediateScalar(2.0, ScalarType.Float, True),
                ImmediateScalar(3.0, ScalarType.Float, False),
                ImmediateScalar(4, ScalarType.Int, True)
                ], True),
            "-(-vec1.x, vec2.x, vec1.y, vec3.w)": UnnamedVectorValue([
                SingleVectorComponent(VarNameBase("vec1"), VectorComponent.x, ScalarType.Untyped, True),
                SingleVectorComponent(VarNameBase("vec2"), VectorComponent.x, ScalarType.Untyped, False),
                SingleVectorComponent(VarNameBase("vec1"), VectorComponent.y, ScalarType.Untyped, False),
                SingleVectorComponent(VarNameBase("vec3"), VectorComponent.w, ScalarType.Untyped, False),
            ], True),
            "vec.xzw": SwizzledVectorValue([
                SingleVectorComponent(VarNameBase("vec"), VectorComponent.x, ScalarType.Untyped, False),
                SingleVectorComponent(VarNameBase("vec"), VectorComponent.z, ScalarType.Untyped, False),
                SingleVectorComponent(VarNameBase("vec"), VectorComponent.w, ScalarType.Untyped, False),
            ], False),
            "-constants[0xFF - 1 + 3.0 - vec.x].xzzy": SwizzledVectorValue([
                SingleVectorComponent(long_index, VectorComponent.x, ScalarType.Untyped, False),
                SingleVectorComponent(long_index, VectorComponent.z, ScalarType.Untyped, False),
                SingleVectorComponent(long_index, VectorComponent.z, ScalarType.Untyped, False),
                SingleVectorComponent(long_index, VectorComponent.y, ScalarType.Untyped, False),
            ], True)
        }

if __name__ == '__main__':
    unittest.main()
