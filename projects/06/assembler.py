#!/usr/bin/env python3

import argparse
import re


# Comment Regex
COMMENT = r"//"  # two forward slashes

# Address Command Regex
ADDRESS_CMD = r"^@\d+$"  # ampersand followed by 1 or more digits

# Label Command Regex
LABEL = r"[a-zA-Z]+\w*"  # Starts with a letter, contains only letters, digits, and underscores
LABEL_CMD = r"^\(" + LABEL + r"\)$"

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


# Jump Patterns

class Parser:
    def __init__(self, filename):
        with open(filename) as f:
            self.filelines = f.readlines()
        self.commands = []

    def command_type(self, command):
        
        match = re.search(ADDRESS_CMD, command)
        if match:
            return 'A_COMMAND'
        
        match = re.search(LABEL_CMD, command)
        if match:
            return 'L_COMMAND'
        
        match = re.search(COMPUTE_CMD, command)
        if match:
            return 'C_COMMAND'
        
        raise SyntaxError(f"Unrecognized command format: {command}")

    def find_commands(self):
        # TODO Add label command filter/processing here:
        for l in self.filelines:
            c = self._remove_comments(l)
            c = self._remove_whitespace(c)
            if self._is_empty_string(c):
                next
            else:
                self.commands.append(c)

    def _remove_comments(self, line):
        return re.split(COMMENT, line, maxsplit=1)[0]

    def _remove_whitespace(self, line):
        return re.sub(r"\s+", "", line)
    
    def _is_empty_string(self, line):
        return line == ""

    def parse_label(self, l_command):
        match = re.search(LABEL, l_command)
        return l_command[match.span()]

    def get_symbol(self, a_command):
        pass

    def get_destinations(self, c_command):
        match = re.search(DESTINATION, c_command)
        if match: 
            dest = c_command[match.start():match.end()]
            return [d for d in ['A', 'M', 'D'] if d in dest]
        else: 
            return None

    def get_jump(self, c_command):
        match = re.search(JUMP, c_command)
        if match:
            return c_command[match.start()+1:]
        else: 
            return None

    def get_compute(self, c_command):
        c_command = re.sub(DESTINATION, "", c_command)
        c_command = re.sub(JUMP, "", c_command)
        # TODO


class Code:
    pass

class SymbolTable:
    pass


if __name__ == "__main__":

    # Initialize CLI Parser, Get Args
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    p = Parser(args.filename)
    p.find_commands()

    for c in p.commands:
        ct = p.command_type(c)
        if ct == 'C_COMMAND':
            d = p.get_destinations(c)
            j = p.get_jump(c)
        else: 
            d=None
            j=None
        print(c, ct, d, j)
        