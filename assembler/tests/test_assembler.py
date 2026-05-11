import unittest
import assembler


class TestSymbolTable(unittest.TestCase):
    def __init__(self):
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
    def __init__(self):
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
            with self.assertRaises:
                actual_command_type = self.parser.command_type(c)

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
            with self.assertRaises:
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
            "JMP",
        ]
        for c in invalid_cmds:
            with self.assertRaises:
                actual_command_type = self.parser.command_type(c)

    def test_parse_address_cmd(self):
        
        commands = [
            "@valid_variable_name",
            "@valid_variable_name$2",
            "@valid_variable_name.2",
            "@123"
        ]
        expected_ouput = [
            ("valid_variable_name", 16),
            ("valid_variable_name$2", 17),
            ("valid_variable_name.2", 18),
            ("123", 123)
        ]
        for i in range(len(commands)):
            command = commands[i]
            expected_name, expected_address = expected_ouput[i]
            actual_name, actual_address = self.parser.parse_address_cmd(command)
            self.assertEqual(expected_name, actual_name)
            self.assertEqual(expected_address, actual_address)

    def test_parse_compute_cmd(self):
        
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
        # Returns the destination (dest), computation (comp) and jump condition 
        # segments of an compute command (with format: 'dest=comp;jump')

        # Parameters
        # ----------
        # command : str 
        #     A compute command (type 'COMPUTE_CMD') from the input file 
            
        # Returns
        # ------
        # dest : str
        #     The text preceding the '=' indicating which registers or memory
        #     locations to store the result. The destinations may include various 
        #     combinations of A, D or M. If no destination is present in the 
        #     command None is returned. 
        # comp : str
        #     The text indicating what computation should be completed. For 
        #     possible computations, see constants.COMP_MNEMONICS. 
        #     Computation commands must contain comp text, so this cannot be 
        #     None. 
        # jump : str
        #     The text after the ';' indicating under what conditions a jump 
        #     should occur. For possible values, see constants.JUMP_MNEMONICS. 
        #     If no jump condition is present in the command None is returned. 


class TestCode(unittest.TestCase):
    def __init__(self):
        pass
        # self.symbol_table = assembler.SymbolTable()

        # # Build Parser
        # self.parser = assembler.Parser(
        #     filepath='tests/fixtures/Rect.asm', 
        #     symbols=self.symbol_table)
        
        # Define Codes and Write to Hack File
        #encoder = assembler.Code(parser=parser)
        #encoder.write_codes(debug=False)

    def test_output_paths(self):
        pass
        # output_filepath : str
        #     The filepath of the output file
        # debug_filepath : str
        #     The filepath of an optional file containing debugging data 
        # parser : Parser
        #     Instance of the Parser class cotaining the parsed input file
        # codes : List[dict]
        #     A list of dicts containing the new binary codes (key: code) for each 
        #     command from the input file and additional command data fields passed 
        #     from the parser. 

        # Methods
        # -------
        # make_address_cmd_binary(self, command: str)
        #     Calls the parser to get the address of an address command then 
        #     converts the address to an addressing binary command
        # make_compute_cmd_binary(self, command: str)
        #     Calls the parser to break a compute command into the destination 
        #     (dest), computation (comp) and jump segments, then looks up and 
        #     assembles their corresponding binaries.
        # write_codes(self, debug: Optional[bool] = False)
        #     Writes the assembled binary commands to the output file and some
        #     additional command data to the the debugging output file if that is 
        #     requested.


class TestIntegration(unittest.TestCase):

    def test_integration(self):
        # File Paths
        input_path = 'tests/fixtures/Rect.asm'
        output_path = 'tests/fixtures/Rect.hack'
        # debug_path = 'tests/fixtures/Rect_debug.hack'
        expect_output_path = 'tests/fixtures/ExpectedRect.hack'
        # expect_debug_path = 'tests/fixtures/ExpectedRect_debug.hack'
        
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
        with open(expect_output_path) as f:
            expect = f.readlines()
        self.assertEqual(actual, expect)

        # with open(debug_path) as f:
        #     actual = f.readlines()
        # with open(expect_debug_path) as f:
        #     expect = f.readlines()
        # self.assertEqual(actual, expect)


if __name__ == "__main__":
    unittest.main()