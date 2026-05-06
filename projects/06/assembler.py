#!/usr/bin/env python3

import argparse
import re
from typing import Optional

import utils
import constants

# Filen Extentions  
INPUT_FILE_EXTENTION = ".asm"
OUTPUT_FILE_EXTENTION = ".hack"

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
DESTINATION = r"^([AMD]+=)"

RESULT_0 = r"0"
RESULT_1 = r"-?1"
RESULT_2 = r"[-!]?[AMD]"
RESULT_3 = r"[AMD][+-][AMD]"
RESULT_4 = r"[AMD][\&\|][AMD]"
RESULT = (
	r"((" + 
    RESULT_0 + r")|(" + 
    RESULT_1 + r")|(" +
    RESULT_2 + r")|(" +
    RESULT_3 + r")|(" +
    RESULT_4 + r")|(" +
    r"))"
)

JUMP_0 = r";JMP$"
JUMP_1 = r";J[GL][TE]$"
JUMP_2 = r";JEQ$"
JUMP_3 = r";JNE$"
JUMP = (r"((" + 
    JUMP_0 + r")|(" + 
    JUMP_1 + r")|(" +
    JUMP_2 + r")|(" +
    JUMP_3 + r"))"
)

COMPUTE_CMD = DESTINATION + r"?" + RESULT + JUMP + r"?"

class SymbolTable:
    def __init__(self, ram_start: int = constants.RAM_START):
        
        self.ram_start = ram_start
        self.ram_symbols = {s: a for s,a in constants.RAM_SYMBOLS.items()}
        self.mmio_symbols = {s: a for s,a in constants.MEM_MAPPED_IO_SYMBOLS.items()}
        self.next_ram_address = max(self.ram_symbols.values()) + 1

        self.symbols = {**self.ram_symbols, **self.mmio_symbols}

    def symbol_exists(self, symbol: str):
        return symbol in self.symbols.keys()

    def insert(self, symbol: str, address:  Optional[int] = None):
        if symbol in self.symbols.keys():
            raise Exception(f"Symbol '{symbol}' previously defined.")

        if address: 
            self.symbols[symbol]=address
        else:
            self.symbols[symbol]=self.next_ram_address
            self.next_ram_address += 1

    def get_address(self, symbol: str):
        if self.symbol_exists(symbol):
            return self.symbols[symbol]
        else: 
            self.insert(symbol)


class Parser:
    def __init__(self, filename: str, symbols: type[SymbolTable] = None):
        self.extract_io_filenames(filename)
        with open(filename) as f:
            self.filelines = f.readlines()
        self.find_commands()
        self.symbols = symbols
        if self.symbols:
            self.update_labels()
            self.resolve_addresses()
    
    def extract_io_filenames(self, filename):
        match = re.search(INPUT_FILE_EXTENTION + '$', filename)
        if not match:
            raise IOError(f"Input filename must be an assembly file ending in '{INPUT_FILE_EXTENTION}' .")
        self.infile = filename
        self.outfile = filename[:-4] + OUTPUT_FILE_EXTENTION

    def find_commands(self):
        self.commands = []
        rom_address=0
        for l in range(len(self.filelines)):
            txt = self.filelines[l]
            txt = self._remove_comments(txt)
            txt = utils.remove_whitespace(txt)
            if utils.is_empty_string(txt):
                continue
            else:
                self.commands.append({
                    'command':txt, 
                    'source_line':l, 
                    'rom_address': rom_address, 
                    'command_type': self.command_type(txt)
                    })
                rom_address += 1
    
    def update_labels(self):
        for entry in self.commands:
            if entry['command_type'] == 'LABEL_CMD':
                self.symbols.insert(entry['command'][1:-1], entry['rom_address'])

    def resolve_addresses(self):
        for entry in self.commands:
            if entry['command_type'] == 'ADDRESS_CMD':
                self.parse_address_cmd(entry['command'])

    def is_label_cmd(self, command: str):
        match = re.search(LABEL_CMD, command)
        return True if match else False

    def is_address_cmd(self, command: str):
        match = re.search(ADDRESS_CMD, command)
        return True if match else False
    
    def is_compute_cmd(self, command: str):
        match = re.search(COMPUTE_CMD, command)
        return True if match else False
    
    def command_type(self, command: str):
        if self.is_label_cmd(command):
            return "LABEL_CMD"
        if self.is_address_cmd(command):
            return "ADDRESS_CMD"
        elif self.is_compute_cmd(command):
            return "COMPUTE_CMD"
        else: 
            raise SyntaxError(f"Unrecognized command format: '{command}'")

    def parse_address_cmd(self, command: str):
        match = re.search(INT_ADDRESS_CMD, command)
        if match: 
            return command[1:], int(command[1:])
        match = re.search(VAR_ADDRESS_CMD, command)
        if match:
            return command[1:], self.symbols.get_address(command[1:])

    def _remove_comments(self, line: str):
        return re.split(COMMENT, line, maxsplit=1)[0]

    def parse_compute_cmd(self, command):
        dest = None
        jump = None
        match = re.search(DESTINATION, command)
        if match: 
            dest = command[match.start():match.end()-1]
            command = command[match.end():]
        match = re.search(JUMP, command)
        if match: 
            jump = command[match.start()+1:]
            command = command[:match.start()]
        comp = command
        return dest, comp, jump


class Code:
    def __init__(self, parser: type[Parser]):
        self.parser = parser
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
                raise Exception(f"Unable to encode line {entry['source_line']} ('{command}') as '{command_type}'.")
            entry['code'] = code
            self.codes.append(entry)

    def make_address_cmd_binary(self, command):
        name, address = self.parser.parse_address_cmd(command)
        return '0' + utils.binary_string_from_int(address, binary_width=constants.MAX_BITS)

    def make_compute_cmd_binary(self, command):
        dest, comp, jump = self.parser.parse_compute_cmd(command)
        dest_bin_str = constants.DEST_MNEMONICS[dest]
        comp_bin_str = constants.COMP_MNEMONICS[comp]
        jump_bin_str = constants.JUMP_MNEMONICS[jump]
        return '111' + comp_bin_str + dest_bin_str + jump_bin_str
    
    def write_codes(self, debug=False):
        with open(self.parser.outfile, 'w') as f:
            f.write(self.codes[0]['code'])
            for entry in self.codes[1:]: 
                f.write('\n' + entry['code'])
        if debug:
            with open('debug_' + self.parser.outfile, 'w') as f:
                for entry in self.codes: 
                    f.write(str(entry) + '\n')


if __name__ == "__main__":

    # Initialize CLI and Get Args
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    # Initialize Symbols Table
    symbol_table = SymbolTable()

    # Build Parser
    parser = Parser(filename=args.filename, symbols=symbol_table)
    
    # Define Codes and Write to Hack File
    encoder = Code(parser=parser)
    encoder.write_codes(debug=False)

