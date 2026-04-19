10 DIM code% 50
20 FOR pass% = 0 TO 3 STEP 3
30   P% = code%
40   [
50   OPT pass%
60   LD A, 42
70   LD HL, &40000
80   LD B, 100
90   .loop
100  LD (HL), A
110  INC HL
120  DJNZ loop
130  RET
140  ]
150 NEXT pass%
160 CALL code%
170 PRINT "Assembler fertig!"
180 END
