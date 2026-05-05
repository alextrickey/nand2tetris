#!/usr/bin/env python3

import argparse
import re
from typing import Optional

import utils
import constants

# Comment Regex
# Comments are created by two forward slashes and all text after will be ignored
COMMENT = r"//"  

# Label Command Regex
# Labels must start with a letter and contain only letters, digits, and underscores
# Labels are created with parentheses (just before the relevant line)
LABEL = r"[a-zA-Z]+[a-zA-Z_\d]*\w*"  
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
            raise SyntaxError(f"Symbol '{symbol}' previously defined.")

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
        with open(filename) as f:
            self.filelines = f.readlines()
        self.commands = []
        self.symbols = symbols
        if self.symbols:
            self.find_rom_commands()
            self.resolve_addresses()
        
    def find_rom_commands(self):
        rom_address=0
        for l in self.filelines:
            c = self._remove_comments(l)
            c = utils.remove_whitespace(c)
            if utils.is_empty_string(c):
                continue
            if self.is_label_cmd(c):
                self.symbols.insert(c[1:-1], rom_address)
                continue
            else:
                self.commands.append(c)
                rom_address += 1
    
    def resolve_addresses(self):
        for c in self.commands:
            if self.is_address_cmd(c):
                self.parse_address(c)

    def is_label_cmd(self, command: str):
        match = re.search(LABEL_CMD, command)
        return True if match else False

    def is_address_cmd(self, command: str):
        match = re.search(ADDRESS_CMD, command)
        return True if match else False
    
    def parse_address_cmd(self, command: str):
        match = re.search(INT_ADDRESS_CMD, command)
        if match: 
            return command[1:], int(command[1:])
        match = re.search(VAR_ADDRESS_CMD, command)
        if match:
            return command[1:], self.symbols.get_address(command[1:])

    def _remove_comments(self, line: str):
        return re.split(COMMENT, line, maxsplit=1)[0]

    def parse_compute_command():
        pass

    def parse_address_command(command, symbol_table):
        pass


class Code:
    def __init__(self, parser: type[Parser], symboltable: type[SymbolTable]):
        self.parser = parser
        self.dests = constants.DEST_MNEMONICS
        self.jumps = constants.JUMP_MNEMONICS
        self.codes = constants.CODE_MNEMONICS

    def make_binary(self, command):
        self.get_dest_code()
        self.get_comp_code()
        self.get_jump_code()
    
    def get_dest_code(self):
        pass

    def get_comp_code():
        pass

    def get_jump_code():
        pass


if __name__ == "__main__":

    # Initialize CLI and Get Args
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    # Initialize Symbols Table
    s = SymbolTable()

    # Initialize Parser and Find Commands
    p = Parser(args.filename, s)

    c = Code(parser=p, symboltable=s)

    for c in p.commands:
        print(c)
        if p.is_address_cmd(c):
             n, a = p.parse_address(c)
             print(n, a)
        print('\n')
        #ct = p.command_type(c)
        #if ct == 'C_COMMAND':
        #    d = p.get_destinations(c)
        #    j = p.get_jump(c)
        #else: 
        #    d=''
        #    j=''
        #print(c, ct, d, j)

    print(s.symbols)
