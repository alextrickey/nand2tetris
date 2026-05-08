import unittest
import assembler


class TestSymbolTable(unittest.TestCase):

    def test_sum(self):
        #self.assertEqual(sum([1, 2, 3]), 6, "Should be 6")
        pass

    def test_sum_tuple(self):
        #self.assertEqual(sum((1, 2, 2)), 6, "Should be 6")
        pass


class TestParser(unittest.TestCase):
    pass


class TestCode(unittest.TestCase):
    pass


class TestIntegration(unittest.TestCase):

    def test_integration(self):
        # File Paths
        input_path = 'tests/fixtures/Rect.asm'
        output_path = 'tests/fixtures/Rect.hack'
        expect_path = 'tests/fixtures/ExpectedRect.hack'
        
        # Initialize Symbols Table
        symbol_table = assembler.SymbolTable()

        # Build Parser
        parser = assembler.Parser(filepath=input_path, symbols=symbol_table)
        
        # Define Codes and Write to Hack File
        encoder = assembler.Code(parser=parser)
        encoder.write_codes(debug=False)

        with open(output_path) as f:
            actual = f.readlines()
        
        with open(expect_path) as f:
            expect = f.readlines()

        self.assertEqual(actual, expect, f"Output ({output_path}) did not match expected ({expect_path}).")


if __name__ == "__main__":
    unittest.main()