// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, 
// the screen should be cleared.

(start)

// Init screen state (white)
@R2
M=0

(reset)

// Init screen index
@SCREEN
D=A
@R1
M=0

// Init screen state (white)
@R2
M=0

(listen.for.keypress)
@KBD
D=M
@press
D;JGT

// If no keypress & black -> whiten screen
// Otherwise listen for press
@R2
D=M
@whiten.screen
D;JGT 
@listen.for.keypress
A;JMP

(press)
// If keypress & white -> blacken screen
// Otherwise listen for press
@R2
D=M
@blacken.screen
D;JEQ
@listen.for.keypress
A;JMP


(blacken.screen)
// Blacken a 16bit block
@R1
D=M
@SCREEN
A=D+A
M=-1

// Increment screen index
@R1
DM=M+1

// Check for end of screen
@8192
D=A-D
@blacken.screen
D;JGT

// Update screen state
@R2
M=1

@reset
A;JMP

(whiten.screen)
// Whiten a 16bit block
@R1
D=M
@SCREEN
A=A+D
M=0

// Increment screen index
@R1
DM=M+1

// Check for end of screen
@8192
D=A-D
@whiten.screen
D;JGT

// Update screen state
@R2
M=0

@reset
A;JMP

(end)
