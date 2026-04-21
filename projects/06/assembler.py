#!/usr/bin/env python3

import argparse

class Parser:
    def __init__(self, filename):
        with open(filename) as f:
            assembly_lines = f.readlines()
        # print(filename)
        # print(assembly_lines[0:10])


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
