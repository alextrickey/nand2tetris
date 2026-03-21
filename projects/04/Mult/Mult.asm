// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
// The algorithm is based on repetitive addition.

// Set R2 to zero
@R2
M = 0
@R3
M = 1

(loop)
// Get next digit of R0
@R0
D = M
@R3 
D = M & D
D = D - M

// If digit is 0 update counters, and jump to next digit
@update
D; JLT

// If digit is 1 add product to total
@R1
D = M
@R2
M = M + D

(update)
// Increment digit
@R3
M = M + 1

// Double R1
@R1
D = M
M = M + D 

// Check end condition
@16
D = M
@R3
D = M - D; 

@end
D; JLT

@loop
JMP 

(end)
