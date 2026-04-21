10 REM schulung/01_paddle_smoke.bas - Syntax-Smoke fuer 01_paddle
15 REM Ruft jede PROC einmal auf, OHNE MODE 8, damit Fehler in stdout
17 REM erscheinen (bei MODE 8 laufen Errors in den VDP und sind headless
19 REM nicht sichtbar).
20 REM USES lib/debug
30 :
40 PROC_dbg_init("")
50 PROC_dbg_log("smoke: init")
60 :
70 REM Globals wie in 01_paddle.bas
80 scrW% = 1280 : scrH% = 1024
90 padW% = 200 : padH% = 24 : padY% = 80 : padSpd% = 40
100 padX% = (scrW% - padW%) / 2
110 quit% = FALSE
120 :
130 PROC_dbg_log("smoke: PROC_fill_rect")
140 PROC_fill_rect(0, 0, 10, 10)
150 :
160 PROC_dbg_log("smoke: PROC_redraw")
170 PROC_redraw(padX%)
180 :
190 PROC_dbg_log("smoke: PROC_tick (1 Frame)")
200 PROC_tick
210 :
220 PRINT "=== TEST PASS ==="
230 PROC_dbg_exit(0)
240 END
250 :
260 REM === Identische Kopie der PROCs aus 01_paddle.bas =========
270 :
280 DEF PROC_fill_rect(x%, y%, w%, h%)
290   MOVE x%, y%
300   PLOT 101, x% + w%, y% + h%
310 ENDPROC
320 :
330 DEF PROC_tick
340   LOCAL k%, oldX%
350   oldX% = padX%
360   k% = INKEY(0)
370   IF k% = 27 THEN quit% = TRUE
380   IF INKEY(-66) THEN padX% = padX% - padSpd%
390   IF INKEY(-51) THEN padX% = padX% + padSpd%
400   IF padX% < 0 THEN padX% = 0
410   IF padX% + padW% > scrW% THEN padX% = scrW% - padW%
420   IF padX% <> oldX% THEN PROC_redraw(oldX%)
430   *FX 19
440 ENDPROC
450 :
460 DEF PROC_redraw(oldX%)
470   GCOL 0, 0
480   PROC_fill_rect(oldX%, padY%, padW%, padH%)
490   GCOL 0, 7
500   PROC_fill_rect(padX%, padY%, padW%, padH%)
510 ENDPROC
