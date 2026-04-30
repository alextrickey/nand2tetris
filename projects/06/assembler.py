#!/usr/bin/env python3

import argparse
import re

import constants

# Comment Regex
COMMENT = r"//"  # two forward slashes

# Label Command Regex
LABEL = r"[a-zA-Z]+[a-zA-Z_\d]*\w*"  # Starts with a letter, contains only letters, digits, and underscores
LABEL_CMD = r"^\(" + LABEL + r"\)$"

# Address Command Regex
ADDRESS_CMD = r"^\@((\d+)|(" + LABEL + r"))$"  # ampersand followed by 1 or more digits

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

    def __init__(self, symbols: dict = constants.SYMBOLS):
        self.symbols = symbols

    def add_symbol(self, symbol: str, address: int):
        self.symbols[symbol]=address


class Parser:
    def __init__(self, filename: str):
        with open(filename) as f:
            self.filelines = f.readlines()
        self.commands = []

    def is_label(self, command: str):
        match = re.search(LABEL_CMD, command)
        return True if match else False

    def command_type(self, command: str):
        
        match = re.search(ADDRESS_CMD, command)
        if match:
            return 'A_COMMAND'
        
        match = re.search(COMPUTE_CMD, command)
        if match:
            return 'C_COMMAND'
        
        raise SyntaxError(f"Unrecognized command format: {command}")


    def find_commands(self, symbols: type[SymbolTable] = None):
        rom_address=0
        for l in self.filelines:
            c = self._remove_comments(l)
            c = self._remove_whitespace(c)
            if self._is_empty_string(c):
                continue
            if self.is_label(c) and symbols:
                symbols.add_symbol(c[1:-1], rom_address)
                continue
            else:
                self.commands.append(c)
                rom_address += 1

    def _remove_comments(self, line: str):
        return re.split(COMMENT, line, maxsplit=1)[0]

    def _remove_whitespace(self, line: str):
        return re.sub(r"\s+", "", line)
    
    def _is_empty_string(self, line: str):
        return line == ""

    def parse_label(self, l_command: str):
        match = re.search(LABEL, l_command)
        return l_command[match.span()]

    def get_destinations(self, c_command: str):
        match = re.search(DESTINATION, c_command)
        if match: 
            dest = c_command[match.start():match.end()]
            return [d for d in ['A', 'M', 'D'] if d in dest]
        else: 
            return None

    def get_jump(self, c_command: str):
        match = re.search(JUMP, c_command)
        if match:
            return c_command[match.start()+1:]
        else: 
            return None

    def get_compute(self, c_command: str):
        c_command = re.sub(DESTINATION, "", c_command)
        c_command = re.sub(JUMP, "", c_command)
        # TODO


class Code:
    def __init__(self, parser: type[Parser]):
        self.parser = parser
        self.dests = constants.DEST_NMEMONICS
        self.jumps = constants.JUMP_NMEMONICS
        self.codes = constants.CODE_NMEMONICS

    def make_binary(self):
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
    p = Parser(args.filename)
    p.find_commands(symbols=s)

    for c in p.commands:
        print(c, p.command_type(c))
        #ct = p.command_type(c)
        #if ct == 'C_COMMAND':
        #    d = p.get_destinations(c)
        #    j = p.get_jump(c)
        #else: 
        #    d=''
        #    j=''
        #print(c, ct, d, j)

    print(s.symbols)
