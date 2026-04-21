10 REM schulung/02_paddle_sprite - Iteration 2: Paddle als Bitmap-Sprite
15 REM Unterschied zu 01: Paddle ist jetzt ein gemaltes 16x16 Sprite
17 REM (02_paddle.rgba, mit sped erstellt) statt ein PLOT-Rechteck.
18 REM Koordinaten sind PHYSISCH (0..319, 0..239), nicht logisch.
19 REM Steuerung: A=links, D=rechts, ESC=beenden
20 REM USES lib/debug
30 :
40 REM === Bildschirmmodus & Tastatur ===========================
45 :
50 MODE 8             : REM 320x240 physisch, 64 Farben, VDP 2.0+
60 VDU 23, 1, 0       : REM Cursor aus
70 *FX 11, 250        : REM Keyboard-Repeat Delay
80 *FX 12, 33         : REM Keyboard-Repeat Rate
90 PROC_dbg_init("")
100 :
110 :
120 REM === Sprite laden =========================================
125 :
130 REM Schritt 1: Bitmap 0 anlegen mit 16x16 Pixeln RGBA8888
140 REM    VDU 23, 27, 0, n     waehlt Bitmap n als "aktiv"
150 REM    VDU 23, 27, 1, w; h; ... liefert w*h*4 Bytes Daten
160 VDU 23, 27, 0, 0
170 VDU 23, 27, 1, 16; 16;
180 :
190 REM Schritt 2: die 1024 Bytes aus der Asset-Datei streamen
200 REM    sped (F=Format 2 RGBA8) hat die Datei mit 16*16*4=1024 Bytes
210 REM    gespeichert, Reihenfolge wird vom VDU-Kommando erwartet.
220 f% = OPENIN "02_paddle.rgba"
230 FOR i% = 1 TO 1024
240   VDU BGET#f%
250 NEXT
260 CLOSE#f%
270 PROC_dbg_log("Bitmap 0 geladen (02_paddle.rgba, 1024 Byte)")
280 :
290 REM Schritt 3: Sprite 0 an Bitmap 0 koppeln und aktivieren
300 REM    VDU 23, 27, 4, n   Select Sprite n
310 REM    VDU 23, 27, 5       Clear frames des aktuellen Sprites
320 REM    VDU 23, 27, 6, b    Add Bitmap b als Frame
330 REM    VDU 23, 27, 11      Sprite einblenden
340 REM    VDU 23, 27, 7, N   Anzahl aktiver Sprites setzen
350 VDU 23, 27, 4, 0
360 VDU 23, 27, 5
370 VDU 23, 27, 6, 0
380 VDU 23, 27, 11
390 VDU 23, 27, 7, 1
400 :
410 :
420 REM === Konstanten in PHYSISCHEN Pixeln =======================
425 REM Iteration 01 rechnete in logischen 1280x1024. Die Sprite-
427 REM API (VDU 23, 27, 13, x;y;) nimmt aber PHYSISCHE Pixel.
429 REM Daher ist scrW% = 320, nicht 1280, und padSpd% = 2, nicht 40.
430 :
440 scrW% = 320
450 scrH% = 240
460 padW% = 16        : REM Sprite-Breite, kommt aus sped
470 padY% = 220       : REM knapp ueber dem unteren Rand
480 padX% = (scrW% - padW%) / 2
490 padSpd% = 2
500 quit% = FALSE
510 :
520 REM Sprite 0 initial an Startposition schieben + Refresh
530 VDU 23, 27, 4, 0
540 VDU 23, 27, 13, padX%; padY%;
550 VDU 23, 27, 15 : REM Sprites sichtbar machen (Double-Buffer Flip)
560 :
570 :
580 REM === Haupt-Loop ===========================================
590 REPEAT
600   PROC_tick
610 UNTIL quit%
620 :
630 :
640 REM === Aufraeumen ===========================================
650 VDU 23, 27, 4, 0
660 VDU 23, 27, 12 : REM Hide Sprite
670 VDU 23, 27, 15 : REM Refresh
680 VDU 23, 1, 1   : REM Cursor wieder an
690 MODE 0
700 PRINT "Programm beendet."
710 PROC_dbg_exit(0)
720 END
730 :
740 :
750 REM === Prozeduren ===========================================
760 :
770 DEF PROC_tick
780   LOCAL k%
790   :
800   REM INKEY(0) fuer ESC, INKEY(-N) fuer A/D (direkter Scan-Code)
810   k% = INKEY(0)
820   IF k% = 27 THEN quit% = TRUE
830   IF INKEY(-66) THEN padX% = padX% - padSpd%
840   IF INKEY(-51) THEN padX% = padX% + padSpd%
850   :
860   REM Clipping am physischen Bildschirmrand
870   IF padX% < 0 THEN padX% = 0
880   IF padX% + padW% > scrW% THEN padX% = scrW% - padW%
890   :
900   REM Sprite 0 auf neue Position schieben. VDU 23, 27, 15 ist
910   REM der "Refresh"-Befehl - ohne ihn wird die Aenderung nicht
920   REM sichtbar, weil der VDP double-buffered arbeitet.
930   VDU 23, 27, 4, 0
940   VDU 23, 27, 13, padX%; padY%;
950   VDU 23, 27, 15
960   :
970   REM VSync-Warten begrenzt den Loop auf 60 fps (wie in 01)
980   *FX 19
990 ENDPROC
