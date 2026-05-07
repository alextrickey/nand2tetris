import unittest
import utils


class TestUtils(unittest.TestCase):

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