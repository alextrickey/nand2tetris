// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, 
// the screen should be cleared.

(start)

// Init screen index
@SCREEN
D=A
@R1
M=0

(listen.for.keypress)


(blacken.screen)
// Blacken a 16bit block
@R1
D=M
@SCREEN
A=A+D
M=-1

// Increment screen index
@R1
DM=M+1

// Check for end of screen
@8192
D=A-D
@blacken.screen
D;JGT

(end)
