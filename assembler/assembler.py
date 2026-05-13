#!/usr/bin/env python3

import argparse
import re
from typing import Optional

import utils
import constants

# File Extentions  
INPUT_FILE_EXTENTION = ".asm"
OUTPUT_FILE_EXTENTION = ".hack"
DEBUG_FILE_EXTENTION = ".debug"

# Comment Regex
# Comments are created by two forward slashes and all text after will be ignored
COMMENT = r"//"  

# Label Command Regex
# Labels must start with a letter and contain only letters, digits, and underscores
# Labels are created with parentheses (just before the relevant line)
LABEL = r"[a-zA-Z]+[a-zA-Z_.$\d]*\w*"  
LABEL_CMD = r"^\(" + LABEL + r"\)$"

# Address Command Regex
# Addresses are specified with an ampersand followed by 1 or more digits or a label
INT_ADDRESS_CMD = r"^\@(\d+)$"  
VAR_ADDRESS_CMD = r"^\@(" + LABEL + r")$"
ADDRESS_CMD = r"^\@((\d+)|(" + LABEL + r"))$"  

# Compute Command Regex ("Destination=Result;Jump")
DESTINATION_PATTERN = r"^([AMD]+=)"
COMPUTATION_PATTERN = utils.regex_any([
    r"0",
    r"-?1",
    r"[-!]?[AMD]",
    r"[AMD][+-][AMD1]",
    r"[AMD][\&\|][AMD]",
])
JUMP_PATTERN = utils.regex_any([
    r";JMP$",
    r";J[GL][TE]$",
    r";JEQ$",
    r";JNE$"
])

COMPUTE_CMD = (
    DESTINATION_PATTERN + r"?" + 
    COMPUTATION_PATTERN + 
    JUMP_PATTERN + r"?$"
)

class SymbolTable:
    """
    Class holding symbol-address mappings and methods to insert, 
    retrieve and check the existence of mappings. 

    Attributes
    ----------
    symbols : dict
        The mapping of text label/variable names (keys) to integer
        ROM/RAM locations (values).
    next_ram_address : int
        The address representing the next available/unused RAM location

    Methods
    -------
    symbol_exists(symbol: str)
        Returns True if the symbol is already in the dict, otherwise
        returns False.
    insert(self, symbol: str, address:  Optional[int] = None)
        Add the specified symbol to the mapping with the provided 
        address if present, otherwise the next available memory location 
        is used. 
    get_address(self, symbol: str)
        Lookup the address for the provided symbol and if none exists 
        create a new address at the next available location in RAM. 

    """
    def __init__(self):
        """Initializes the symbol mapping using defaults for RAM and Memory Mapped IO 
         devices. Sets the next available RAM address."""
        self._ram_symbols = {s: a for s,a in constants.RAM_SYMBOLS.items()}
        self._mmio_symbols = {s: a for s,a in constants.MEM_MAPPED_IO_SYMBOLS.items()}
        self.next_ram_address = max(self._ram_symbols.values()) + 1
        self.symbols = {**self._ram_symbols, **self._mmio_symbols}

    def symbol_exists(self, symbol: str):
        """Looks up the specified symbol in the table and returns True if the 
        symbol is present, otherwise returns False.
        
        Parameters
        ----------
        symbol : str 
            Name of the variable or label to be checked

        Returns
        ----------
        bool
            True if the symbol is present, otherwise False
        """
        return symbol in self.symbols.keys()

    def insert(self, symbol: str, address:  Optional[int] = None):
        """Add the specified symbol to the mapping with the provided 
        address if present, otherwise the next available memory location 
        is used.
        
        Parameters
        ----------
        symbol : str 
            Name of the variable or label to be added
        address : Optional[int] 
            The integer value of the memory location to associate with 
            the new symbol. If None is provided, the address will be 
            set to the next available RAM location. 
            
        Raises
        ------
        Exception
            If the symbol to be added is already in the mapping.
        """
        if symbol in self.symbols.keys():
            raise Exception(f"Symbol '{symbol}' previously defined.")

        if address: 
            self.symbols[symbol]=address
        else:
            self.symbols[symbol]=self.next_ram_address
            self.next_ram_address += 1

    def get_address(self, symbol: str):
        """Add the specified symbol to the mapping with the provided 
        address if present, otherwise the next available memory location 
        is used. 
        
        Parameters
        ----------
        symbol : str 
            Name of the variable or label
            
        Returns
        ------
        int
            The address of RAM location assigned to the provided symbol
        """
        if self.symbol_exists(symbol):
            return self.symbols[symbol]
        else: 
            self.insert(symbol)
            return self.symbols[symbol]


class Parser:
    """
    Class to process syntax in an assembly file to identify commands, 
    map symbols to addresses, determine parts of computations and 
    raise errors if malformed codes are provided.

    Attributes
    ----------
    input_filepath : str
        The filepath of the input file
    symbols : SymbolTable
        Instance of the SymbolTable class to contain default and
        file-specific symbols, variable names, labels and their
        corresponding addresses
    commands : List[dict]
        A list of dicts containing data about each line of the input
        that contains a meaningful command. The dict has the following
        keys: 
            command: Text of the command without comments/whitespase 
            source_line: The line number of the command in the input file
            rom_address: The line number that will represent the command 
                in the output file
            command_type: String indicating the type of the command
                LABEL_CMD: Provides a new label via '(LABEL_NAME)'
                ADDRESS_CMD: Sets A to an address via '@ADDRESS' or '@SYMBOL'
                COMPUTE_CMD: Indicates a computation with an optional 
                    destination and jump condition via: 'dest=computation;jump'

    Methods
    -------
    command_type(command: str)
        Returns the type of command 
    parse_address_cmd(command: str):
        Returns the label/variable name and the address of an address 
        command
    parse_compute_cmd(command: str):
        Returns the destination (dest), computation (comp) and jump condition 
        segments of an compute command (with format: 'dest=comp;jump')

    """
    def __init__(self, filepath: str, symbols: type[SymbolTable] = None):
        """Checks the filepath, sets the input, output and debugging
        filepaths, then parses the lines of input file into commands and 
        symbols.
        
        Parameters
        ----------
        filepath : str 
            Filepath of the input file including the filename and extention
            
        Raises
        ------
        Exception
            If the file does not have the correct assembly extention ('.a).
        """
        # Check and Set Filepath Attributes
        self._check_file_type(filepath)
        self.input_filepath = filepath

        # Read input file and find commands
        with open(filepath) as f:
            self.filelines = f.readlines()
        self._find_commands()

        # Process symbols for labels/variables
        self.symbols = symbols
        if self.symbols:
            self._update_labels()
            self._resolve_addresses()
    
    def _check_file_type(self, filepath):
        """Ensures that the file path includes path extention
        
        Parameters
        ----------
        filepath : str 
            Filepath with filename (including extention)
            
        Raises
        ------
        Exception
            If the file is not assembly or doesn't have the correct extention.
        """
        match = re.search(INPUT_FILE_EXTENTION + '$', filepath)
        if not match:
            raise Exception(f"Input filename must be an assembly file ending in "
                          f"'{INPUT_FILE_EXTENTION}' .")

    def _find_commands(self):
        """Processes the input into commands by stripping comments, 
        whitespace and empty lines, then determines the type of command, 
        counts relevant ROM commands and logs these in the commands dict
        """
        self.commands = []
        rom_address=0
        for l in range(len(self.filelines)):
            txt = self.filelines[l]
            txt = self._remove_comments(txt)
            txt = utils.remove_whitespace(txt)
            if utils.is_empty_string(txt):
                continue
            command_type = self.command_type(txt)
            self.commands.append({
                'command':txt, 
                'source_line':l, 
                'rom_address': rom_address, 
                'command_type': command_type
                })
            if command_type != 'LABEL_CMD':
                rom_address += 1
    
    def _remove_comments(self, line: str):
        """Removes comments which may be whole lines or at the end of a line

        Parameters
        ----------
        line : str 
            The current line of text from the input file to be processed
            
        Returns
        ------
        str
            The line of text without any text occurring after the comment 
            characters
        """
        return re.split(COMMENT, line, maxsplit=1)[0]
        
    def _update_labels(self):
        """Adds new labels identified in the input file to the SymbolTable"""
        for entry in self.commands:
            if entry['command_type'] == 'LABEL_CMD':
                self.symbols.insert(entry['command'][1:-1], entry['rom_address'])

    def _resolve_addresses(self):
        """Adds new variables identified in the input file to the SymbolTable
        by setting the address to the next available RAM location (if none exists 
        from defaults or provided labels)"""
        for entry in self.commands:
            if entry['command_type'] == 'ADDRESS_CMD':
                self.parse_address_cmd(entry['command'])
    
    def command_type(self, command: str):
        """Returns the type of command 

        Parameters
        ----------
        command : str 
            A command identified from the input file
            
        Returns
        ------
        str
            LABEL_CMD if the command has format: '(LABEL_NAME)'
            ADDRESS_CMD if the command has format: '@ADDRESS' or '@SYMBOL'
            COMPUTE_CMD if the comment specifies a computation of form
                'dest=computation;jump' where dest and jump are optional
        """
        if re.match(LABEL_CMD, command):
            return "LABEL_CMD"
        if re.match(ADDRESS_CMD, command):
            return "ADDRESS_CMD"
        elif re.match(COMPUTE_CMD, command):
            return "COMPUTE_CMD"
        else: 
            raise SyntaxError(f"Unrecognized command format: '{command}'")

    def parse_address_cmd(self, command: str):
        """Returns the label/variable name and the address of an address 
        command

        Parameters
        ----------
        command : str 
            A address command (type: 'ADDRESS_CMD') from the input file 
            
        Returns
        ------
        name : str
            The text of the label, variable name or raw address in the 
            command. 
        address : int
            The address retrieved from the SymbolTable or the raw 
            address if provided
        """
        command_type = self.command_type(command)
        if command_type != "ADDRESS_CMD":
            raise Exception(
                f"Address parsing requires an ADDRESS_CMD, "
                f"received {self.command_type}"
                )

        match = re.match(INT_ADDRESS_CMD, command)
        if match: 
            return command[1:], int(command[1:])
        match = re.match(VAR_ADDRESS_CMD, command)
        if match:
            return command[1:], self.symbols.get_address(command[1:])

    def parse_compute_cmd(self, command: str):
        """Returns the destination (dest), computation (comp) and jump condition 
        segments of an compute command (with format: 'dest=comp;jump')

        Parameters
        ----------
        command : str 
            A compute command (type 'COMPUTE_CMD') from the input file 
            
        Returns
        ------
        dest : str
            The text preceding the '=' indicating which registers or memory
            locations to store the result. The destinations may include various 
            combinations of A, D or M. If no destination is present in the 
            command None is returned. 
        comp : str
            The text indicating what computation should be completed. For 
            possible computations, see constants.COMP_MNEMONICS. 
            Computation commands must contain comp text, so this cannot be 
            None. 
        jump : str
            The text after the ';' indicating under what conditions a jump 
            should occur. For possible values, see constants.JUMP_MNEMONICS. 
            If no jump condition is present in the command None is returned. 
        """
        command_type = self.command_type(command)
        if command_type != "COMPUTE_CMD":
            raise Exception(
                f"Computation parsing requires a COMPUTE_CMD, "
                f"received {self.command_type}"
                )
        
        dest = None
        jump = None
        match = re.match(DESTINATION_PATTERN, command)
        if match: 
            dest = command[match.start():match.end()-1]
            command = command[match.end():]
        match = re.search(JUMP_PATTERN, command)
        if match: 
            jump = command[match.start()+1:]
            command = command[:match.start()]
        comp = command
        return dest, comp, jump


class Code:
    """
    Class to use parser to assemble the binaries of commands in the parsed 
    file

    Attributes
    ----------
    output_filepath : str
        The filepath of the output file
    debug_filepath : str
        The filepath of an optional file containing debugging data 
    parser : Parser
        Instance of the Parser class cotaining the parsed input file
    codes : List[dict]
        A list of dicts containing the new binary codes (key: code) for each 
        command from the input file and additional command data fields passed 
        from the parser. 

    Methods
    -------
    make_address_cmd_binary(self, command: str)
        Calls the parser to get the address of an address command then 
        converts the address to an addressing binary command
    make_compute_cmd_binary(self, command: str)
        Calls the parser to break a compute command into the destination 
        (dest), computation (comp) and jump segments, then looks up and 
        assembles their corresponding binaries.
    write_codes(self, debug: Optional[bool] = False)
        Writes the assembled binary commands to the output file and some
        additional command data to the the debugging output file if that is 
        requested.
    """
    def __init__(self, parser: type[Parser]):
        """Sets the parser, output_file, and debug_file attributes then 
        calls methods to compute binaries for each parsed command and stores
        these in the codes attribute. 

        Parameters
        ----------
        command : str 
            An address command (type 'ADDRESS_CMD') from the input file 
            
        Raises
        ------
        Exception 
            If the command type is not recognized
        """
        self.parser = parser

        self.output_filepath = (
            self.parser.input_filepath[:-4] + OUTPUT_FILE_EXTENTION)
        self.debug_filepath = (
            self.parser.input_filepath[:-4] + DEBUG_FILE_EXTENTION)

        self.codes = []
        for entry in parser.commands:
            command = entry['command']
            command_type = entry['command_type']
            if command_type == 'ADDRESS_CMD':
                code = self.make_address_cmd_binary(command)
            elif command_type == 'COMPUTE_CMD':
                code = self.make_compute_cmd_binary(command)
            elif command_type == 'LABEL_CMD':
                continue
            else:
                raise Exception(f"Unable to encode '{command}' as '{command_type}'.")
            entry['code'] = code
            self.codes.append(entry)

    def make_address_cmd_binary(self, command: str):
        """Calls the parser to get the address of an address command then 
        converts the address to an addressing binary command

        Parameters
        ----------
        command : str 
            An address command (type 'ADDRESS_CMD') from the input file 
            
        Returns
        ------
        str
            The binary command for the address represented with a string
        """
        name, address = self.parser.parse_address_cmd(command)
        return '0' + utils.binary_string_from_int(address, binary_width=constants.MAX_BITS)

    def make_compute_cmd_binary(self, command: str):
        """Calls the parser to break a compute command into the destination 
        (dest), computation (comp) and jump segments, then looks up and 
        assembles their corresponding binaries.

        Parameters
        ----------
        command : str 
            A compute command (type 'COMPUTE_CMD') from the input file
            
        Returns
        ------
        str
            The corresponding binary command for the specified computation
        """
        
        dest, comp, jump = self.parser.parse_compute_cmd(command)
        dest_bin_str = constants.DEST_MNEMONICS[dest]
        comp_bin_str = constants.COMP_MNEMONICS[comp]
        jump_bin_str = constants.JUMP_MNEMONICS[jump]
        return '111' + comp_bin_str + dest_bin_str + jump_bin_str
    
    def write_codes(self, debug: Optional[bool] = False):
        """Writes the assembled binary commands to the output file and some
        additional command data to the the debugging output file if that is 
        requested.

        Parameters
        ----------
        debug : Optional[bool] 
            Writes the debugging file if set to True, [default: False]
        """
        with open(self.output_filepath, 'w') as f:
            f.write(self.codes[0]['code'])
            for entry in self.codes[1:]: 
                f.write('\n' + entry['code'])
        if debug:
            with open(self.debug_filepath, 'w') as f:
                for entry in self.codes: 
                    f.write(str(entry) + '\n')


if __name__ == "__main__":

    # Initialize CLI and Get Args
    cli_arg_parser = argparse.ArgumentParser()
    cli_arg_parser.add_argument('filepath')
    cli_arg_parser.add_argument('-d', '--debug', action='store_true')
    args = cli_arg_parser.parse_args()

    # Initialize Symbols Table
    symbol_table = SymbolTable()

    # Build Parser
    parser = Parser(filepath=args.filepath, symbols=symbol_table)
    
    # Define Codes and Write to Hack File
    translator = Code(parser=parser)
    translator.write_codes(debug=args.debug)
