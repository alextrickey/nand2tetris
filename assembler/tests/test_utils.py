import unittest
from assembler import utils


class TestUtils(unittest.TestCase):
    
    def test_remove_whitespace(self):

        input = 'no   s pa \n\t ce'
        actual = utils.remove_whitespace(line=input)
        expect = 'nospace'
        self.assertEqual(actual, expect, "Observed: {actual}, Expected: {expect}")
    
    def test_is_empty_string(self):

        self.assertTrue(utils.is_empty_string(line=''))
        self.assertFalse(utils.is_empty_string(line=' '))
    
    def test_regex_any(self):

        input = ['a', 'b', 'c']
        actual = utils.regex_any(input)
        expect = '((a)|(b)|(c))'
        self.assertEqual(actual, expect, "Observed: {actual}, Expected: {expect}")

        input = ['a']
        actual = utils.regex_any(input)
        expect = '((a))'
        self.assertEqual(actual, expect, "Observed: {actual}, Expected: {expect}")

        input = []
        actual = utils.regex_any(input)
        expect = '(())'
        self.assertEqual(actual, expect, "Observed: {actual}, Expected: {expect}")

    def test_binary_string_from_int(self):
        
        actual = utils.binary_string_from_int(value=3)
        expect = '11'
        self.assertEqual(actual, expect, "Observed: {actual}, Expected: {expect}")

        actual = utils.binary_string_from_int(value=3, binary_width=4)
        expect = '0011'
        self.assertEqual(actual, expect, "Observed: {actual}, Expected: {expect}")

        with self.assertRaises(Exception):
            utils.binary_string_from_int(value=4, binary_width=2)


if __name__ == "__main__":
    unittest.main()