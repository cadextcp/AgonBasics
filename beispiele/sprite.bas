10 REM Sprite-Beispiel: Ship
20 MODE 8
30 REM --- Bitmap 0 laden (16x16 RGBA8888) ---
40 VDU 23, 27, 0, 0 : REM Select Bitmap 0
50 VDU 23, 27, 1, 16; 16;
60 f% = OPENIN "ship.rgba"
70 FOR i% = 1 TO 1024
80   VDU BGET#f%
90 NEXT : CLOSE#f%
100 REM --- Sprite 0 erstellen ---
110 VDU 23, 27, 4, 0 : REM Select Sprite 0
120 VDU 23, 27, 5 : REM Clear frames
130 VDU 23, 27, 6, 0 : REM Add Bitmap 0
140 VDU 23, 27, 11 : REM Show Sprite
150 VDU 23, 27, 7, 1 : REM Activate 1 sprite
160 REM --- Sprite positionieren ---
170 x% = 152 : y% = 104
180 VDU 23, 27, 13, x%; y%;
190 VDU 23, 27, 15 : REM Refresh
200 REM --- Steuerung mit WASD ---
210 REPEAT
220   k% = INKEY(5)
230   IF k% = ASC("w") AND y% > 0 y% = y% - 2
240   IF k% = ASC("s") AND y% < 224 y% = y% + 2
250   IF k% = ASC("a") AND x% > 0 x% = x% - 2
260   IF k% = ASC("d") AND x% < 304 x% = x% + 2
270   VDU 23, 27, 4, 0
280   VDU 23, 27, 13, x%; y%;
290   VDU 23, 27, 15
300 UNTIL k% = 27
310 REM --- Aufraeumen ---
320 VDU 23, 27, 4, 0
330 VDU 23, 27, 12 : REM Hide Sprite
340 VDU 23, 27, 15 : REM Refresh
350 MODE 0
