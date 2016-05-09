import unittest
from unittest import TestCase

from src.main.fr.tagc.wopmars.framework.rule.Option import Option


class TestOption(TestCase):
    def setUp(self):
        self.__option_string1 = Option("option1", "value1")
        self.__option_string2 = Option("option1", "value1")
        self.__option_string3 = Option("option1", "value2")

        self.__option_int1 = Option("option3", "1")
        self.__option_int2 = Option("option3", "1")
        self.__option_int3 = Option("option3", "2")

        self.__option_float1 = Option("option5", "1.1")
        self.__option_float2 = Option("option5", "1.1")
        self.__option_float3 = Option("option5", "2.2")

        self.__option_bool1 = Option("option7", True)
        self.__option_bool2 = Option("option7", True)
        self.__option_bool3 = Option("option7", False)

    def test_correspond(self):
        self.assertTrue(self.__option_string1.correspond("str"))
        self.assertTrue(self.__option_string1.correspond("bool"))
        self.assertFalse(self.__option_string1.correspond("int"))
        self.assertFalse(self.__option_string1.correspond("float"))

        self.assertTrue(self.__option_int1.correspond("str"))
        self.assertTrue(self.__option_int1.correspond("int"))
        self.assertTrue(self.__option_int1.correspond("float"))
        self.assertTrue(self.__option_int1.correspond("bool"))

        self.assertTrue(self.__option_float1.correspond("str"))
        self.assertFalse(self.__option_float1.correspond("int"))
        self.assertTrue(self.__option_float1.correspond("float"))
        self.assertTrue(self.__option_float1.correspond("bool"))

        self.assertTrue(self.__option_bool1.correspond("str"))
        self.assertTrue(self.__option_bool1.correspond("int"))
        self.assertTrue(self.__option_bool1.correspond("float"))
        self.assertTrue(self.__option_bool1.correspond("bool"))

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