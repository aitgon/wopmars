import unittest
from unittest import TestCase
from wopmars.models.Option import Option
from wopmars.utils.WopMarsException import WopMarsException


class TestOption(TestCase):

    def setUp(self):
        self.__option_string1 = Option(name="option1", value="value1")
        self.__option_string2 = Option(name="option1", value="value1")
        self.__option_string3 = Option(name="option1", value="value2")

        self.__option_int1 = Option(name="option3", value="1")
        self.__option_int2 = Option(name="option3", value="1")
        self.__option_int3 = Option(name="option3", value="2")

        self.__option_float1 = Option(name="option5", value="1.1")
        self.__option_float2 = Option(name="option5", value="1.1")
        self.__option_float3 = Option(name="option5", value="2.2")

        self.__option_bool1 = Option(name="option7", value=True)
        self.__option_bool2 = Option(name="option7", value=True)
        self.__option_bool3 = Option(name="option7", value=False)

    def test_correspond(self):
        try:
            self.__option_string1.correspond("str")
            self.__option_string1.correspond("bool")
        except:
            raise AssertionError("Souldn't raise an exception.")
        self.assertRaises(WopMarsException, self.__option_string1.correspond, "int")
        self.assertRaises(WopMarsException, self.__option_string1.correspond, "float")

        try:
            self.__option_int1.correspond("str")
            self.__option_int1.correspond("int")
            self.__option_int1.correspond("float")
            self.__option_int1.correspond("bool")
        except:
            raise AssertionError("Shouldn't raise an exception.")

        try:
            self.__option_float1.correspond("str")
            self.__option_float1.correspond("float")
            self.__option_float1.correspond("bool")
        except:
            raise AssertionError("Shouldn't raise an exception.")
        self.assertRaises(WopMarsException, self.__option_float1.correspond, "int")

        try:
            self.__option_bool1.correspond("str")
            self.__option_bool1.correspond("int")
            self.__option_bool1.correspond("float")
            self.__option_bool1.correspond("bool")
        except:
            raise AssertionError("Shouldn't raise an exception.")

    def test_eq(self):
        self.assertEqual(self.__option_string1, self.__option_string2)
        self.assertNotEqual(self.__option_string1, self.__option_string3)
        self.assertNotEqual(self.__option_string1, self.__option_int3)

        self.assertEqual(self.__option_int1, self.__option_int2)
        self.assertNotEqual(self.__option_int1, self.__option_int3)
        self.assertNotEqual(self.__option_int1, self.__option_string3)

        self.assertEqual(self.__option_float1, self.__option_float2)
        self.assertNotEqual(self.__option_float1, self.__option_float3)
        self.assertNotEqual(self.__option_float1, self.__option_string3)

        self.assertEqual(self.__option_bool1, self.__option_bool2)
        self.assertNotEqual(self.__option_bool1, self.__option_bool3)
        self.assertNotEqual(self.__option_bool1, self.__option_string3)

if __name__ == "__main__":
    unittest.main()