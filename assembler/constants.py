#########################################
# Computation Nmemonic to Code Mappings #
#########################################

# Computation Command Format Fed to ALU:  111a cccc ccdd djjj
# where the a, c's, d's and j's are defined below.

# Destinations
# Code format = d1 d2 d3
# - if d1=1 then store result in Register A
# - if d2=1 then store result in Register D
# - if d3=1 then store result in Memory location addressed in A

DEST_MNEMONICS = {
    # Assign to all three locations
    'AMD': '111',
    'ADM': '111',
    'MDA': '111',
    'MAD': '111',
    'DMA': '111',
    'DAM': '111',

    # Assign to two locations
    'AM': '101',
    'MA': '101',
    'AD': '110',
    'DA': '110',
    'MD': '011',
    'DM': '011',

    # Assign to one location
    'A': '100',
    'M': '001',
    'D': '010',

    # No assignment
    None: '000'
}

# Jump Conditions
# Code format = j1 j2 j3
# - if j1=1 then jump if result is less than 0
# - if j2=1 then jump if result equals 0
# - if j3=1 then jump if result is greater than 0

JUMP_MNEMONICS = {
    None:  '000',  # Don't Jump
    'JGT': '001',  # Jump if Greater Than 0
    'JEQ': '010',  # Jump if Equal to 0
    'JGE': '011',  # Jump if Greater than or Equal to 0
    'JLT': '100',  # Jump if Less than 0
    'JNE': '101',  # Jump if Not Equal to 0
    'JLE': '110',  # Jump if Less than or Equal to 0
    'JMP': '111',  # Jump unconditionally
}

# ALU Operations 
# Code format = a c1 c2 c3 c4 c5 c6
# - if a=0 then A is used for the computation, otherwise M is used
# 
# The c codes are inputs to the ALU 
# and have the following meanings: 
# - if c1=1 the first ALU input (D) is set to 0
# - if c2=1 the first ALU input (D) is negated
# - if c3=1 the second ALU input (A or M) is set to 0
# - if c4=1 the second ALU input (A or M) is negated
# - if c5=1 the computation is arithmetic (+) otherwise logical (&)
# - if c6=1 the computation result is negated
#
# For further detail, reference the ALU component HDL and 
# the Nand2Tetris documentation. 
COMP_MNEMONICS = {
    '0':    '0' + '101010',
    '1':    '0' + '111111',
    '-1':   '0' + '111010',
    'D':    '0' + '001100',
    'A':    '0' + '110000',
    'M':    '1' + '110000',
    '!D':   '0' + '001101',
    '!A':   '0' + '110001',
    '!M':   '1' + '110001',
    '-D':   '0' + '001111',
    '-A':   '0' + '110011',
    '-M':   '1' + '110011',
    'D+1':  '0' + '011111',
    'A+1':  '0' + '110111',
    'M+1':  '1' + '110111',
    'D-1':  '0' + '001110',
    'A-1':  '0' + '110010',
    'M-1':  '1' + '110010',
    'D+A':  '0' + '000010',
    'D+M':  '1' + '000010',
    'D-A':  '0' + '010011',
    'D-M':  '1' + '010011',
    'A-D':  '0' + '000111',
    'M-D':  '1' + '000111',
    'D&A':  '0' + '000000',
    'D&M':  '1' + '000000',
    'D|A':  '0' + '010101',
    'D|M':  '1' + '010101',
}

######################
# Predefined Symbols #
######################
RAM_START = 0
MAX_BITS = 15

RAM_SYMBOLS = {
    'SP':     RAM_START + 0,
    'LCL':    RAM_START + 1,
    'ARG':    RAM_START + 2,
    'THIS':   RAM_START + 3,
    'THAT':   RAM_START + 4,
    'R0':     RAM_START + 0,
    'R1':     RAM_START + 1,
    'R2':     RAM_START + 2,
    'R3':     RAM_START + 3,
    'R4':     RAM_START + 4,
    'R5':     RAM_START + 5,
    'R6':     RAM_START + 6,
    'R7':     RAM_START + 7,
    'R8':     RAM_START + 8,
    'R9':     RAM_START + 9,
    'R10':    RAM_START + 10,
    'R11':    RAM_START + 11,
    'R12':    RAM_START + 12,
    'R13':    RAM_START + 13,
    'R14':    RAM_START + 14,
    'R15':    RAM_START + 15,
}
    
MEM_MAPPED_IO_SYMBOLS = {
    'SCREEN': 16384,
    'KBD':    24576,
}