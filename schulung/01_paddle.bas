10 REM schulung/01_paddle - Iteration 1: nur das Paddle zeichnen und bewegen
15 REM Lernziel: MODE 8, Game-Loop, INKEY-Input, partielles Redraw, ESC-Exit
17 REM Steuerung: A=links, D=rechts, ESC=beenden
19 REM Siehe 01_paddle.md fuer detaillierte Erklaerungen.
20 REM USES lib/debug
30 :
40 REM === Bildschirmmodus & Tastatur ===========================
45 :
50 MODE 8 : REM 320x240 physisch, 64 Farben, logische Flaeche 1280x1024
60 :
70 VDU 23, 1, 0 : REM Cursor ausblenden (23,1,0 = Cursor off)
80 :
90 REM Keyboard-Repeat beschleunigen, damit A/D-Gedrueckthalten glatt laeuft
100 REM *FX 11,N setzt Delay bis Repeat beginnt (N*10ms, Default 320ms)
110 REM *FX 12,N setzt Repeat-Rate (N*10ms, Default 80ms)
130 *FX 11, 250
140 *FX 12, 33
150 :
160 REM Debug-Library initialisieren (druckt "[dbg] init t=0 log=-")
170 PROC_dbg_init("")
180 :
190 :
200 REM === Konstanten ==========================================
205 :
210 REM --- Bildschirmgroessen (logisch) ---
220 scrW% = 1280 : REM Breite
230 scrH% = 1024 : REM Hoehe
240 :
250 REM --- Paddle ---
260 padW% = 200 : REM Breite ~15 Prozent der Bildschirmbreite
270 padH% = 24  : REM Hoehe
280 padY% = 80  : REM Y-Position; BBC-BASIC-Origin ist LINKS UNTEN,
282 REM             also sitzt das Paddle weit unten im Bild.
290 padSpd% = 40: REM Bewegungsschritt pro Tick (1 Frame = 1/60 s)
300 :
310 :
320 REM === Initialzustand ======================================
325 :
330 REM Paddle startet mittig am unteren Rand
340 padX% = (scrW% - padW%) / 2
350 :
360 REM Abbruch-Flag. Wird in PROC_tick auf TRUE gesetzt, wenn ESC kommt.
370 quit% = FALSE
380 :
390 :
400 REM === Initialzeichnung ====================================
405 :
410 REM Schirm einfarbig schwarz wischen, dann Paddle weiss malen.
420 GCOL 0, 0 : CLG
430 GCOL 0, 7 : PROC_fill_rect(padX%, padY%, padW%, padH%)
440 :
450 :
460 REM === Haupt-Loop ==========================================
465 :
470 REM Eine Frame pro Durchlauf. PROC_tick kuemmert sich um alles:
475 REM Input lesen, Paddle bewegen, clippen, neu zeichnen, VSync abwarten.
480 REPEAT
490   PROC_tick
500 UNTIL quit%
510 :
520 :
530 REM === Aufraeumen ==========================================
535 :
540 VDU 23, 1, 1 : REM Cursor wieder einblenden
550 MODE 0       : REM zurueck in den 80-Spalten-Textmodus
560 PRINT "Programm beendet."
570 :
580 REM Sauberer Exit - in der headless-Version schaltet PROC_dbg_exit
582 REM den Emulator ab; im GUI landen wir am BBC-BASIC-Prompt.
590 PROC_dbg_exit(0)
600 END
610 :
620 :
630 REM ============================================================
640 REM == Prozeduren ==============================================
650 REM ============================================================
660 :
670 :
680 REM --- PROC_fill_rect ---------------------------------------
690 REM Zeichnet ein gefuelltes Rechteck in der aktuell per GCOL
700 REM gesetzten Grafikfarbe. MOVE setzt den Startpunkt (unten-links),
710 REM PLOT 101 zieht nach oben-rechts und FUELLT automatisch.
720 REM Docs: https://agonplatform.github.io/agon-docs/vdp/PLOT-Commands/
730 DEF PROC_fill_rect(x%, y%, w%, h%)
740   MOVE x%, y%
750   PLOT 101, x% + w%, y% + h%
760 ENDPROC
770 :
780 :
790 REM --- PROC_tick --------------------------------------------
800 REM Ein Frame: Input -> Move -> Clip -> Redraw -> VSync.
810 REM Wird vom Haupt-Loop pro Durchlauf einmal aufgerufen.
820 DEF PROC_tick
830   LOCAL k%, oldX%
840   :
850   REM Alte X-Position merken, um das Paddle dort gleich schwarz
852   REM ueberzumalen.
860   oldX% = padX%
870   :
880   REM INKEY(0) holt sich das naechste Zeichen aus dem Tastatur-Puffer
882   REM (oder -1 wenn keins da ist). Wir pruefen hier nur auf ESC = 27.
890   k% = INKEY(0)
900   IF k% = 27 THEN quit% = TRUE
910   :
920   REM INKEY(-N) prueft direkt, ob Taste mit Scancode N gerade
922   REM gedrueckt wird (TRUE/FALSE). A = 66, D = 51 (BBC-Micro-Layout,
924   REM 1:1 auf FabGL gemappt). Siehe docs/REFERENCE.md.
930   IF INKEY(-66) THEN padX% = padX% - padSpd%
940   IF INKEY(-51) THEN padX% = padX% + padSpd%
950   :
960   REM Clipping: Paddle darf nicht ueber den Rand hinaus.
970   IF padX% < 0 THEN padX% = 0
980   IF padX% + padW% > scrW% THEN padX% = scrW% - padW%
990   :
1000   REM Nur wenn sich die Position geaendert hat neu zeichnen.
1010   REM Spart Flackern und Rechenzeit.
1020   IF padX% <> oldX% THEN PROC_redraw(oldX%)
1030   :
1040   REM *FX 19 wartet auf den naechsten VSync-Puls (~60 Hz).
1045   REM Damit laeuft unser Loop auf genau 1 Frame / 16.67 ms,
1050   REM unabhaengig von der CPU-Geschwindigkeit.
1060   *FX 19
1070 ENDPROC
1080 :
1090 :
1100 REM --- PROC_redraw ------------------------------------------
1110 REM Altes Paddle (an Position oldX%) wegwischen, neues Paddle
1120 REM (an aktueller Position padX%) zeichnen.
1130 REM Hintergrundfarbe 0 = schwarz, Vordergrundfarbe 7 = weiss.
1140 DEF PROC_redraw(oldX%)
1150   REM 1) Altes Paddle mit Hintergrundfarbe ueberzeichnen
1160   GCOL 0, 0
1170   PROC_fill_rect(oldX%, padY%, padW%, padH%)
1180   :
1190   REM 2) Neues Paddle weiss zeichnen
1200   GCOL 0, 7
1210   PROC_fill_rect(padX%, padY%, padW%, padH%)
1220 ENDPROC
