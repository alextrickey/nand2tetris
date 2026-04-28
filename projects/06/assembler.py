#!/usr/bin/env python3

import argparse
import re


# Comment Regex
COMMENT = r"//"  # two forward slashes


# Jump Patterns

class Parser:
    def __init__(self, filename):
        with open(filename) as f:
            self.filelines = f.readlines()
        self.commands = []
        self.next = 0

    def has_more_commands(self):
        return self.next < len(self.commands) - 1

    def advance(self):
        if self.has_more_commands():
            self.command = self.commands[self.next]
            self.linei += 1
        else: 
            print('End of file')

    def find_commands(self):
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

    for l in p.commands:
        print(l)