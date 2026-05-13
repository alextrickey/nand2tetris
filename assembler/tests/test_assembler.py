import unittest
import assembler


class TestSymbolTable(unittest.TestCase):
    def setUp(self):
        self.symbol_table = assembler.SymbolTable()
    
    def test_default_symbols(self):

        # Check that some standard symbols are populated
        self.assertIn('KBD', self.symbol_table.symbols.keys())
        self.assertIn('SCREEN', self.symbol_table.symbols.keys())
        self.assertIn('R0', self.symbol_table.symbols.keys())
        self.assertIn('THAT', self.symbol_table.symbols.keys())

    def test_initial_next_ram(self):
        initial_next_ram = 16
        self.assertEqual(self.symbol_table.next_ram_address, initial_next_ram)

    def test_symbol_exists(self):
        input_symbol = 'KBD'
        self.assertTrue(self.symbol_table.symbol_exists(input_symbol))
        input_symbol = 'fake'
        self.assertFalse(self.symbol_table.symbol_exists(input_symbol))
        input_symbol = None
        self.assertFalse(self.symbol_table.symbol_exists(input_symbol))

    def test_insertion(self):
        initial_next_ram = 16

        # Insertion without address
        new_symbol = 'new1'
        new_address = None
        self.symbol_table.insert(symbol=new_symbol, address=new_address)
        self.assertTrue(self.symbol_table.symbol_exists(new_symbol))
        actual = self.symbol_table.symbols[new_symbol]
        expect = initial_next_ram 
        self.assertEqual(actual, expect)

        # Next RAM address after insert
        new_next_ram = initial_next_ram + 1
        self.assertEqual(self.symbol_table.next_ram_address, new_next_ram)

        # Insertion with given address
        new_symbol = 'new2'
        new_address = 55
        self.symbol_table.insert(symbol=new_symbol, address=new_address)
        self.assertTrue(self.symbol_table.symbol_exists(new_symbol))
        actual = self.symbol_table.symbols[new_symbol]
        expect = 55
        self.assertEqual(actual, expect)
        
        # Insertion should fail if symbol exists
        with self.assertRaises(Exception):
            previously_defined_symbol = 'new2'
            another_address = 58
            self.symbol_table.insert(symbol=previously_defined_symbol, 
                                     address=another_address)

        # Current behavior is next RAM does not update in response to 
        # adding higher RAM address [Enhancement opportunity]
        new_next_ram = initial_next_ram + 1
        self.assertEqual(self.symbol_table.next_ram_address, new_next_ram)

    def test_get_address(self):
        # Get address with existing symbol
        existing_symbol = 'new1'
        expected_address = 16
        actual_address = self.symbol_table.get_address(existing_symbol)
        self.assertEqual(actual_address, expected_address)

        # Get address with non-existing symbol
        non_existing_symbol = 'new3'
        expected_address = 17
        actual_address = self.symbol_table.get_address(non_existing_symbol)
        self.assertEqual(actual_address, expected_address)


class TestParser(unittest.TestCase):
    def setUp(self):
        self.symbol_table = assembler.SymbolTable()

        # Build Parser
        self.parser = assembler.Parser(
            filepath='tests/fixtures/Rect.asm', 
            symbols=self.symbol_table)

    def test_command_type__label(self):
        expected_command_type = "LABEL_CMD"
        valid_cmds = [
            "(valid_label_name)",
            "(valid_label_name$2)",
            "(valid_variable_name.2)",
        ]
        for c in valid_cmds:
            actual_command_type = self.parser.command_type(c)
            self.assertEqual(actual_command_type, expected_command_type)

        invalid_cmds = [
            "(2invalid_address)",
            "(123)",
            "(123.2)",
            "(_invalid)",
            "($invalid)",
        ]
        for c in invalid_cmds:
            with self.assertRaises(Exception):
                actual_command_type = self.parser.command_type(c)
                print(c, actual_command_type)

    def test_command_type__address(self):
        expected_command_type = "ADDRESS_CMD"
        valid_cmds = [
            "@valid_variable_name",
            "@valid_variable_name$2",
            "@valid_variable_name.2",
            "@123"
        ]
        for c in valid_cmds:
            actual_command_type = self.parser.command_type(c)
            self.assertEqual(actual_command_type, expected_command_type)

        invalid_cmds = [
            "@2invalid_address",
            "@123.2",
            "@_invalid",
            "@$invalid",
        ]
        for c in invalid_cmds:
            with self.assertRaises(Exception):
                actual_command_type = self.parser.command_type(c)

    def test_command_type__compute(self):
        expected_command_type = "COMPUTE_CMD"
        valid_cmds = [
            "A=D+A;JMP",
            "ADM=!A;JLE",
            "0",
            "0;JMP",
            "A=M+D",
        ]
        for c in valid_cmds:
            actual_command_type = self.parser.command_type(c)
            self.assertEqual(actual_command_type, expected_command_type)

        invalid_cmds = [
            "JMP",
            "Q=D+A;JLE",
            "A=(A+D)|M",
        ]
        for c in invalid_cmds:
            with self.assertRaises(Exception):
                actual_command_type = self.parser.command_type(c)

    def test_parse_address_cmd(self):
        
        test_cases = [
            {'command': '@valid_name',   'output': ("valid_name", 18)},
            {'command': '@valid_name$2', 'output': ("valid_name$2", 19)},
            {'command': '@valid_name.2', 'output': ("valid_name.2", 20)},
            {'command': '@123',          'output': ("123", 123)},
        ]
        for test_case in test_cases:
            command = test_case['command']
            expected_name, expected_address = test_case['output']
            actual_name, actual_address = self.parser.parse_address_cmd(command)
            self.assertEqual(expected_name, actual_name)
            self.assertEqual(expected_address, actual_address)

        not_address_cmds = [
            "A=D+A;JMP",
            "ADM=!A;JLE",
            "0",
            "0;JMP",
            "A=M+D",
            "(label_name)",
            "(label_name$2)",
            "(variable_name.2)",
        ]
        for c in not_address_cmds:
            with self.assertRaises(Exception):
                unparsable = self.parser.parse_address_cmd(c)

    def test_parse_compute_cmd(self):
        
        test_cases = [
            {'command': 'A=D+A;JMP',  'output': ('A', 'D+A', 'JMP')},
            {'command': 'ADM=!A;JLE', 'output': ('ADM', '!A', 'JLE')},
            {'command': '0',          'output': (None, '0', None)},
            {'command': '0;JMP',      'output': (None, '0', 'JMP')},
            {'command': 'A=M+D',      'output': ('A', 'M+D', None)},
        ]
        for test_case in test_cases:
            command = test_case['command']
            expected_dest, expected_comp, expected_jump = test_case['output']
            dest, comp, jump = self.parser.parse_compute_cmd(command)
            self.assertEqual(expected_dest, dest)
            self.assertEqual(expected_comp, comp)
            self.assertEqual(expected_jump, jump)
        
        not_compute_cmds = [
            "@variable_name",
            "@variable_name$2",
            "@variable_name.2",
            "@123",
            "(label_name)",
            "(label_name$2)",
            "(variable_name.2)",
        ]
        for c in not_compute_cmds:
            with self.assertRaises(Exception):
                unparsable = self.parser.parse_compute_cmd(c)


class TestCode(unittest.TestCase):
    def setUp(self):
        self.symbol_table = assembler.SymbolTable()

        # Build Parser
        self.parser = assembler.Parser(
            filepath='tests/fixtures/Rect.asm', 
            symbols=self.symbol_table)
        
        # Define Codes and Write to Hack File
        self.translator = assembler.Code(parser=self.parser)

    def test_output_paths(self):
        self.assertEqual(self.translator.output_filepath, 'tests/fixtures/Rect.hack')
        self.assertEqual(self.translator.debug_filepath, 'tests/fixtures/Rect.debug')

    def test_address_cmd_binary(self):
        test_cases = [
            {'command': '@valid_name',   'expected': '0000000000010010'},
            {'command': '@valid_name$2', 'expected': '0000000000010011'},
            {'command': '@123',          'expected': '0000000001111011'},
        ]
        for test_case in test_cases:
            c = test_case['command']
            actual = self.translator.make_address_cmd_binary(c)
            self.assertEqual(actual, test_case['expected'])

        invalid_address_cmds = [
            "A=D+A;JMP",
            "ADM=!A;JLE",
            "0",
            "0;JMP",
            "A=M+D",
            "(label_name)",
            "(label_name$2)",
            "(variable_name.2)",
        ]

        for c in invalid_address_cmds:
            with self.assertRaises(Exception):
                self.translator.make_address_cmd_binary(c)
    
    def test_make_compute_cmd_binary(self):
        test_cases = [
            {'command': 'A=D+A;JNE',  'expected': '1110000010100101'},
            {'command': 'ADM=!A;JLE', 'expected': '1110110001111110'},
            {'command': '0',          'expected': '1110101010000000'},
            {'command': '0;JMP',      'expected': '1110101010000111'},
            {'command': 'A=D+M',      'expected': '1111000010100000'},
        ]
        for test_case in test_cases:
            c = test_case['command']
            actual = self.translator.make_compute_cmd_binary(c)
            self.assertEqual(actual, test_case['expected'])

        invalid_compute_cmds = [
            "@variable_name",
            "@variable_name$2",
            "@variable_name.2",
            "@123",
            "(label_name)",
            "(label_name$2)",
            "(variable_name.2)",
        ]

        for c in invalid_compute_cmds:
            with self.assertRaises(Exception):
                self.translator.make_compute_cmd_binary(c)

    def test_write_codes(self):
        # File Paths
        input_path = 'tests/fixtures/Rect.asm'

        output_path = 'tests/fixtures/Rect.hack'
        expect_output_path = 'tests/fixtures/ExpectedRect.hack'

        debug_path = 'tests/fixtures/Rect.debug'
        expect_debug_path = 'tests/fixtures/ExpectedRect.debug'
        
        # Initialize Symbols Table
        symbol_table = assembler.SymbolTable()

        # Build Parser
        parser = assembler.Parser(filepath=input_path, 
                                  symbols=symbol_table)
        
        # Define Codes and Write to Hack File
        translator = assembler.Code(parser=parser)
        translator.write_codes(debug=True)

        with open(output_path) as f:
            actual = f.readlines()
        with open(expect_output_path) as f:
            expect = f.readlines()
        self.assertEqual(actual, expect)

        with open(debug_path) as f:
            actual = f.readlines()
        with open(expect_debug_path) as f:
            expect = f.readlines()
        self.assertEqual(actual, expect)


if __name__ == "__main__":
    unittest.main()