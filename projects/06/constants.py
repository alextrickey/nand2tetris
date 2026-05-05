

##########################
# Code Nmemonic Mappings #
##########################

DEST_MNEMONICS = {
    'AMD': '111',
    'ADM': '111',
    'MDA': '111',
    'MAD': '111',
    'DMA': '111',
    'DAM': '111',

    'AM': '101',
    'MA': '101',
    'AD': '110',
    'DA': '110',
    'MD': '011',
    'DM': '011',

    'A': '100',
    'M': '001',
    'D': '010',
}


# Format: 'LEG'
JUMP_MNEMONICS = {
    None:  '000',
    'JGT': '001',
    'JEQ': '010',
    'JGE': '011',
    'JLT': '100',
    'JNE': '101',
    'JLE': '110',
    'JMP': '111',
}

# Format:   'acccccc'
CODE_MNEMONICS = {
    '0':    '0101010',
    '1':    '0111111',
    '-1':   '0111010',
    'D':    '0001100',
    'A':    '0110000',
    'M':    '1110000',
    '!D':   '0001101',
    '!A':   '0110001',
    '!M':   '1110001',
    '-D':   '0001111',
    '-A':   '0110011',
    '-M':   '1110011',
    'D+1':  '0011111',
    'A+1':  '0110111',
    'M+1':  '1110111',
    'D-1':  '0001111',
    'A-1':  '0110010',
    'M-1':  '1110010',
    'D+A':  '0000010',
    'D+M':  '1000010',
    'D-A':  '0010011',
    'D-M':  '1010011',
    'A-D':  '0000111',
    'M-D':  '1000111',
    'D&A':  '0000000',
    'D&M':  '1000000',
    'D|A':  '0010101',
    'D|M':  '1010101',
}

######################
# Predefined Symbols #
######################
RAM_START = 1024

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