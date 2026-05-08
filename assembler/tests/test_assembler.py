import unittest
import assembler


class TestSymbolTable(unittest.TestCase):

    
    def test_symbol_table(self):
        symbol_table = assembler.SymbolTable()

        # Check that some standard symbols are populated
        self.assertIn('KBD', symbol_table.symbols.keys())
        self.assertIn('SCREEN', symbol_table.symbols.keys())
        self.assertIn('R0', symbol_table.symbols.keys())
        self.assertIn('THAT', symbol_table.symbols.keys())

        # Check initial next RAM address
        initial_next_ram = 16
        self.assertEqual(symbol_table.next_ram_address, initial_next_ram)

        # Check symbol_exists
        input_symbol = 'KBD'
        self.assertTrue(symbol_table.symbol_exists(input_symbol))
        input_symbol = 'fake'
        self.assertFalse(symbol_table.symbol_exists(input_symbol))
        input_symbol = None
        self.assertFalse(symbol_table.symbol_exists(input_symbol))

        # Check insert without address
        new_symbol = 'new1'
        new_address = None
        symbol_table.insert(symbol=new_symbol, address=new_address)
        self.assertTrue(symbol_table.symbol_exists(new_symbol))
        actual = symbol_table.symbols[new_symbol]
        expect = initial_next_ram 
        self.assertEqual(actual, expect)

        # Check next RAM address after insert
        new_next_ram = initial_next_ram + 1
        self.assertEqual(symbol_table.next_ram_address, new_next_ram)

        # Check insert with given address
        new_symbol = 'new2'
        new_address = 55
        symbol_table.insert(symbol=new_symbol, address=new_address)
        self.assertTrue(symbol_table.symbol_exists(new_symbol))
        actual = symbol_table.symbols[new_symbol]
        expect = 55
        self.assertEqual(actual, expect)
        
        # Check insert fails if symbol exists
        with self.assertRaises(Exception):
            previously_defined_symbol = 'new2'
            another_address = 58
            symbol_table.insert(symbol=previously_defined_symbol, 
                                address=another_address)

        # Current behavior is next RAM does not update in response to 
        # adding higher RAM address [Enhancement opportunity]
        new_next_ram = initial_next_ram + 1
        self.assertEqual(symbol_table.next_ram_address, new_next_ram)

        # Check get address with existing symbol
        existing_symbol = 'new1'
        expected_address = 16
        actual_address = symbol_table.get_address(existing_symbol)
        self.assertEqual(actual_address, expected_address)

        # Check get address with non-existing symbol
        non_existing_symbol = 'new3'
        expected_address = 17
        actual_address = symbol_table.get_address(non_existing_symbol)
        self.assertEqual(actual_address, expected_address)



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
        parser = assembler.Parser(filepath=input_path, 
                                  symbols=symbol_table)
        
        # Define Codes and Write to Hack File
        encoder = assembler.Code(parser=parser)
        encoder.write_codes(debug=False)

        with open(output_path) as f:
            actual = f.readlines()
        
        with open(expect_path) as f:
            expect = f.readlines()

        self.assertEqual(actual, expect)


if __name__ == "__main__":
    unittest.main()