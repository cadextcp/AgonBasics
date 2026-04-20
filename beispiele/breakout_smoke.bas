10 REM breakout_smoke.bas - ruft alle PROCs von breakout einmal auf
15 REM ohne MODE 8, damit Syntax-Fehler in stdout auftauchen.
20 REM USES lib/debug
30 :
40 PROC_dbg_init("")
50 PROC_dbg_log("smoke: init")
60 :
70 REM --- Globals setzen (wie breakout.bas) ---
80 scrW% = 1280 : scrH% = 1024
90 padW% = 200 : padH% = 24 : padY% = 80
100 padX% = (scrW% - padW%) / 2
110 ballR% = 16
120 ballX% = scrW% / 2 : ballY% = scrH% / 3
130 ballDX% = 16 : ballDY% = -16
140 nCols% = 8 : nRows% = 5
150 DIM blocks%(nCols%, nRows%)
160 blkGap% = 8
170 blkW% = (scrW% - nCols% * blkGap%) / nCols%
180 blkH% = 48
190 blkYTop% = scrH% - 60
200 FOR c% = 0 TO nCols% - 1 : FOR r% = 0 TO nRows% - 1 : blocks%(c%, r%) = 1 : NEXT : NEXT
210 blkLeft% = nCols% * nRows%
220 score% = 0 : lives% = 3
230 PROC_dbg_log("smoke: globals ok")
240 :
250 REM --- PROC-Aufrufe (ohne MODE, also keine echten VDU-Effekte) ---
260 PROC_dbg_log("smoke: PROC_fill_rect")
270 PROC_fill_rect(0, 0, 10, 10)
280 PROC_dbg_log("smoke: PROC_erase_rect")
290 PROC_erase_rect(0, 0, 10, 10)
300 PROC_dbg_log("smoke: PROC_draw_block")
310 PROC_draw_block(0, 0)
320 PROC_dbg_log("smoke: PROC_bounce_left")
330 PROC_bounce_left
340 PROC_dbg_log("smoke: PROC_bounce_right")
350 PROC_bounce_right
360 PROC_dbg_log("smoke: PROC_bounce_top")
370 PROC_bounce_top
380 PROC_dbg_log("smoke: PROC_paddle_hit")
390 PROC_paddle_hit
400 PROC_dbg_log("smoke: PROC_ball_verloren")
410 PROC_ball_verloren
420 PROC_dbg_log("smoke: PROC_block_hit")
430 PROC_block_hit
440 PROC_dbg_log("smoke: PROC_draw_blocks")
450 PROC_draw_blocks
460 :
470 PRINT "=== TEST PASS ==="
480 PROC_dbg_exit(0)
490 END
500 :
510 REM === hier folgt der PROC-Anteil aus breakout.bas ===
520 :
530 DEF PROC_fill_rect(x%, y%, w%, h%)
540 MOVE x%, y%
550 PLOT 101, x% + w%, y% + h%
560 ENDPROC
570 :
580 DEF PROC_erase_rect(x%, y%, w%, h%)
590 GCOL 0, 0
600 PROC_fill_rect(x%, y%, w%, h%)
610 ENDPROC
620 :
630 DEF PROC_draw_blocks
640 LOCAL c%, r%
650 FOR c% = 0 TO nCols% - 1
660   FOR r% = 0 TO nRows% - 1
670     IF blocks%(c%, r%) = 1 THEN PROC_draw_block(c%, r%)
680   NEXT
690 NEXT
700 ENDPROC
710 :
720 DEF PROC_draw_block(c%, r%)
730 LOCAL bx%, by%, col%
740 bx% = c% * (blkW% + blkGap%) + blkGap% / 2
750 by% = blkYTop% - r% * (blkH% + blkGap%) - blkH%
760 col% = 1 + (r% MOD 6)
770 GCOL 0, col%
780 PROC_fill_rect(bx%, by%, blkW%, blkH%)
790 ENDPROC
800 :
810 DEF PROC_ball_verloren
820 lives% = lives% - 1
830 ballX% = scrW% / 2
840 ballY% = scrH% / 3
850 ballDX% = 16
860 ballDY% = -16
870 ENDPROC
880 :
890 DEF PROC_paddle_hit
900 LOCAL rel%
910 ballDY% = ABS(ballDY%)
920 ballY% = padY% + padH% + ballR% + 1
930 rel% = ballX% - (padX% + padW% / 2)
940 ballDX% = rel% / 6
950 IF ballDX% = 0 THEN ballDX% = 4
960 IF ballDX% > 28 THEN ballDX% = 28
970 IF ballDX% < -28 THEN ballDX% = -28
980 ENDPROC
990 :
1000 DEF PROC_block_hit
1010 LOCAL c%, r%, bx%, by%
1020 FOR c% = 0 TO nCols% - 1
1030   FOR r% = 0 TO nRows% - 1
1040     IF blocks%(c%, r%) = 0 THEN 1140
1050     bx% = c% * (blkW% + blkGap%) + blkGap% / 2
1060     by% = blkYTop% - r% * (blkH% + blkGap%) - blkH%
1070     IF ballX% + ballR% < bx% THEN 1140
1080     IF ballX% - ballR% > bx% + blkW% THEN 1140
1090     IF ballY% + ballR% < by% THEN 1140
1100     IF ballY% - ballR% > by% + blkH% THEN 1140
1110     PROC_block_destroy(c%, r%)
1120     r% = nRows% : c% = nCols%
1140   NEXT
1150 NEXT
1160 ENDPROC
1170 :
1180 DEF PROC_block_destroy(c%, r%)
1190 LOCAL bx%, by%
1200 bx% = c% * (blkW% + blkGap%) + blkGap% / 2
1210 by% = blkYTop% - r% * (blkH% + blkGap%) - blkH%
1220 blocks%(c%, r%) = 0
1230 blkLeft% = blkLeft% - 1
1240 score% = score% + 10
1250 ballDY% = -ballDY%
1260 ENDPROC
1270 :
1280 DEF PROC_bounce_left
1290 ballX% = ballR%
1300 ballDX% = ABS(ballDX%)
1310 ENDPROC
1320 :
1330 DEF PROC_bounce_right
1340 ballX% = scrW% - ballR%
1350 ballDX% = -ABS(ballDX%)
1360 ENDPROC
1370 :
1380 DEF PROC_bounce_top
1390 ballY% = scrH% - ballR%
1400 ballDY% = -ABS(ballDY%)
1410 ENDPROC
