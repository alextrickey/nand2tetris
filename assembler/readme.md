# Assembler

## Overview
This directory contains a python module to parse an assembly script and
assemble the relevant binary codes to create a ROM script that can be run 
on the HACK hardware defined under `../hardware_definition`.

Example assembly files (`.asm`) and binary files (`.hack`) can be found
in the `examples` directory and detailed specifications for each can be 
found in the [Nand2Tetris resource](https://www.nand2tetris.org). 

In brief, the assembler supports three common assembly command types: 
### 1. Labeling
Syntax: `(LABEL)` where `LABEL` is a variable name/symbol which will 
indicate the ROM address of the next relevant command. 

Labels only create symbols that can be referenced lat addressing and do 
not themselves result in any binary command. 

### 2. Addressing
Syntax: `@address` where `address` can be an integer indicating a 
RAM location or a compliant variable/label name. A variable name can  
reference existing symbol with an address defined elsewhere the assembly 
file or the standard set (defined in `constants.RAM_SYMBOLS`). Alternatively, 
it can define a new variable at the next available RAM address. 

The generated machine code has format: ```0vvv vvvv vvvv vvvv``` where the 
leading zero indicates an address is being provided and the remaing `v`s 
can be `0` or `1`, such that they provide an integer address. 


### 3. Computations
Syntax: `dest=comp;jump` where 
    - `dest` indicates the destination where the result of the computation 
    should be stored. It can be any combination of A, D, M where A and D
    are registers and M is the memory at the address in the A register. 
    This component is optional and if no destination is provided the 
    computation result will not be stored. 
    - `comp` indicates the computation to be completed, which can include
    simple arithmetic computations (e.g. `A+D`, `D-M`, and `-A`) and 
    bitwise logical operations (e.g. `A&D`, `A|D`, `!A`). This component 
    is required. 
    - `jump` indicates what computation results should trigger a jump 
    to the ROM line stored in the A register. An unconditional jump can
    be specified with `JMP`, while other codes will compare computation 
    result to zero jump if it greater than/less than or equal to zero 
    (e.g. `JGT`, `JLT`, `JEQ`, `JLE`)

The generated machine code has format: ```111a cccc ccdd djjj``` where the 
3 leading ones indicate the a, c, d, and j bits define a computation. 
Detailed descriptions of the mnemonic to code mappings can be viewed 
in `assembler/constants.py`.


## Setup 
Assembler was tested in Python 3.9 and uses only standard libraries. 

## Running the Assembler
To build binaries for an assembly (`.asm`) file navigate to the assembler
directory and then call the function on desired file. For example, 
to build the binaries for the file 'example/Add.asm': 

```bash
cd path/to/assembler
./assembler.py example/Add.asm
```

The above will build the binary file `Add.hack` in the directory in the 
`example` directory. 

To build both the binary and write an additional debugging file containing 
further information about each command, use the `--debug` flag. 
```bash
cd path/to/assembler
./assembler.py example/Add.asm --debug 
```

## Running Tests
Navigate to the assembler directory run unittest:
```bash
cd path/to/assembler
python3 -m unittest discover tests/
```
