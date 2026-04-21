10 REM breakout.bas - Einfaches Breakout fuer Agon BBC BASIC
15 REM Paddle mit A/D bewegen, ESC beendet. Zerstoere alle Bloecke.
17 REM USES lib/debug
20 :
30 MODE 8 : REM 320x240 physisch, 1280x1024 logisch, 64 Farben
40 VDU 23, 1, 0 : REM Cursor aus
50 PROC_dbg_init("")
60 PROC_dbg_log("Breakout startet")
70 :
80 REM --- Logische Schirmkoordinaten ---
90 scrW% = 1280
100 scrH% = 1024
110 :
120 REM --- Paddle ---
130 padW% = 200
140 padH% = 24
150 padY% = 80
160 padX% = (scrW% - padW%) / 2
170 padSpd% = 40
180 :
190 REM --- Ball ---
200 ballR% = 16
210 ballX% = scrW% / 2
220 ballY% = scrH% / 3
230 ballDX% = 16
240 ballDY% = -16
250 :
260 REM --- Blockfeld ---
270 nCols% = 8
280 nRows% = 5
290 DIM blocks%(nCols%, nRows%)
300 blkGap% = 8
310 blkW% = (scrW% - nCols% * blkGap%) / nCols%
320 blkH% = 48
330 blkYTop% = scrH% - 60
340 FOR c% = 0 TO nCols% - 1
350   FOR r% = 0 TO nRows% - 1
360     blocks%(c%, r%) = 1
370   NEXT
380 NEXT
390 blkLeft% = nCols% * nRows%
400 :
410 score% = 0
420 lives% = 3
430 quit% = FALSE
440 :
450 REM --- Initialzeichnung ---
460 GCOL 0, 0 : CLG
470 PROC_draw_blocks
480 :
490 REM === Haupt-Loop ===
510 REPEAT
512   PROC_game_tick
890 UNTIL quit% OR lives% <= 0 OR blkLeft% <= 0
900 :
910 VDU 23, 1, 1
920 MODE 0
930 IF blkLeft% = 0 THEN PRINT "Gewonnen! Score: "; STR$(score%) ELSE PRINT "Game Over. Score: "; STR$(score%)
940 END
950 :
960 REM ===== Prozeduren =====
970 :
980 DEF PROC_fill_rect(x%, y%, w%, h%)
990 MOVE x%, y%
1000 PLOT 101, x% + w%, y% + h%
1010 ENDPROC
1020 :
1030 DEF PROC_erase_rect(x%, y%, w%, h%)
1040 GCOL 0, 0
1050 PROC_fill_rect(x%, y%, w%, h%)
1060 ENDPROC
1070 :
1080 DEF PROC_draw_blocks
1090 LOCAL c%, r%
1100 FOR c% = 0 TO nCols% - 1
1110   FOR r% = 0 TO nRows% - 1
1120     IF blocks%(c%, r%) = 1 THEN PROC_draw_block(c%, r%)
1130   NEXT
1140 NEXT
1150 ENDPROC
1160 :
1170 DEF PROC_draw_block(c%, r%)
1180 LOCAL bx%, by%, col%
1190 bx% = c% * (blkW% + blkGap%) + blkGap% / 2
1200 by% = blkYTop% - r% * (blkH% + blkGap%) - blkH%
1210 col% = 1 + (r% MOD 6)
1220 GCOL 0, col%
1230 PROC_fill_rect(bx%, by%, blkW%, blkH%)
1240 ENDPROC
1250 :
1260 DEF PROC_ball_verloren
1270 lives% = lives% - 1
1280 ballX% = scrW% / 2
1290 ballY% = scrH% / 3
1300 ballDX% = 16
1310 ballDY% = -16
1320 PROC_dbg_log("Leben: " + STR$(lives%))
1330 ENDPROC
1340 :
1350 DEF PROC_paddle_hit
1360 LOCAL rel%
1370 ballDY% = ABS(ballDY%)
1380 ballY% = padY% + padH% + ballR% + 1
1390 rel% = ballX% - (padX% + padW% / 2)
1400 ballDX% = rel% / 6
1410 IF ballDX% = 0 THEN ballDX% = 4
1420 IF ballDX% > 28 THEN ballDX% = 28
1430 IF ballDX% < -28 THEN ballDX% = -28
1440 ENDPROC
1450 :
1460 DEF PROC_block_hit
1470 LOCAL c%, r%, bx%, by%
1480 FOR c% = 0 TO nCols% - 1
1490   FOR r% = 0 TO nRows% - 1
1500     IF blocks%(c%, r%) = 0 THEN 1600
1510     bx% = c% * (blkW% + blkGap%) + blkGap% / 2
1520     by% = blkYTop% - r% * (blkH% + blkGap%) - blkH%
1530     IF ballX% + ballR% < bx% THEN 1600
1540     IF ballX% - ballR% > bx% + blkW% THEN 1600
1550     IF ballY% + ballR% < by% THEN 1600
1560     IF ballY% - ballR% > by% + blkH% THEN 1600
1570     PROC_block_destroy(c%, r%)
1580     r% = nRows% : c% = nCols% : REM Schleifen beenden
1600   NEXT
1610 NEXT
1620 ENDPROC
1630 :
1640 DEF PROC_block_destroy(c%, r%)
1650 LOCAL bx%, by%
1660 bx% = c% * (blkW% + blkGap%) + blkGap% / 2
1670 by% = blkYTop% - r% * (blkH% + blkGap%) - blkH%
1680 blocks%(c%, r%) = 0
1690 blkLeft% = blkLeft% - 1
1700 score% = score% + 10
1710 ballDY% = -ballDY%
1720 PROC_erase_rect(bx%, by%, blkW%, blkH%)
1730 PROC_dbg_log("block " + STR$(c%) + "," + STR$(r%) + " weg; left=" + STR$(blkLeft%))
1740 ENDPROC
1750 :
1760 DEF PROC_bounce_left
1770 ballX% = ballR%
1780 ballDX% = ABS(ballDX%)
1790 ENDPROC
1800 :
1810 DEF PROC_bounce_right
1820 ballX% = scrW% - ballR%
1830 ballDX% = -ABS(ballDX%)
1840 ENDPROC
1850 :
1860 DEF PROC_bounce_top
1870 ballY% = scrH% - ballR%
1880 ballDY% = -ABS(ballDY%)
1890 ENDPROC
1900 :
1910 DEF PROC_game_tick
1920 LOCAL k%
1930 oldPX% = padX%
1940 oldBX% = ballX%
1950 oldBY% = ballY%
1960 :
1970 REM --- Input ---
1980 k% = INKEY(0)
1990 IF k% = ASC("a") OR k% = ASC("A") THEN padX% = padX% - padSpd%
2000 IF k% = ASC("d") OR k% = ASC("D") THEN padX% = padX% + padSpd%
2010 IF k% = 27 THEN quit% = TRUE
2020 IF padX% < 0 THEN padX% = 0
2030 IF padX% + padW% > scrW% THEN padX% = scrW% - padW%
2040 :
2050 REM --- Ball bewegen ---
2060 ballX% = ballX% + ballDX%
2070 ballY% = ballY% + ballDY%
2080 :
2090 REM --- Wand-Kollisionen ---
2100 IF ballX% < ballR% THEN PROC_bounce_left
2110 IF ballX% > scrW% - ballR% THEN PROC_bounce_right
2120 IF ballY% > scrH% - ballR% THEN PROC_bounce_top
2130 :
2140 REM --- Boden verlassen = Leben ab ---
2150 IF ballY% < 0 THEN PROC_ball_verloren
2160 :
2170 REM --- Paddle-Kollision ---
2180 IF ballDY% < 0 AND ballY% <= padY% + padH% + ballR% AND ballY% >= padY% - ballR% AND ballX% >= padX% - ballR% AND ballX% <= padX% + padW% + ballR% THEN PROC_paddle_hit
2190 :
2200 REM --- Block-Kollision ---
2210 PROC_block_hit
2220 :
2230 REM --- Redraw nur Ball + Paddle ---
2240 PROC_erase_rect(oldPX%, padY%, padW%, padH%)
2250 PROC_erase_rect(oldBX% - ballR%, oldBY% - ballR%, 2 * ballR%, 2 * ballR%)
2260 GCOL 0, 7 : PROC_fill_rect(padX%, padY%, padW%, padH%)
2270 GCOL 0, 3 : PROC_fill_rect(ballX% - ballR%, ballY% - ballR%, 2 * ballR%, 2 * ballR%)
2280 :
2290 REM --- auf VSync warten (OSBYTE 19, einziges unterstuetztes OSBYTE auf Agon) ---
2300 *FX 19
2310 ENDPROC
