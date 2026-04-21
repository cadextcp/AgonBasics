30000 REM === AgonBasics lib/debug.bas ==========================
30010 REM Debug- und Trace-Hilfen fuer BBC BASIC auf Agon Light.
30020 REM
30030 REM Diese Datei enthaelt ausschliesslich PROC-/FN-Definitionen
30040 REM ab Zeile 30000. Anhaengen an das eigene Programm (das mit
30050 REM END abschliessen sollte), dann sind alle PROCs/FNs nutzbar.
30060 REM
30070 REM Uebersicht:
30080 REM   PROC_dbg_init(logfile$)      Init + optional Logdatei oeffnen
30090 REM   PROC_dbg_close               Logdatei schliessen
30100 REM   PROC_dbg_trace(lbl$, val)    Traceausgabe "[t] lbl = val"
30110 REM   PROC_dbg_log(msg$)           Freie Textzeile ausgeben+loggen
30120 REM   PROC_dbg_assert(cond, msg$)  Bei cond=0: PRINT msg$, === TEST FAIL ===,
30125 REM                                Emulator mit exit-code 1 beenden
30130 REM   PROC_dbg_bp(id%)             Emulator-Breakpoint (OUT &10)
30140 REM   PROC_dbg_regs(id%)           CPU-Zustand dumpen (OUT &20)
30150 REM   PROC_dbg_exit(code%)         Emulator beenden (OUT &00)
30151 REM                                Wenn dbg_hold% <> 0 gesetzt ist,
30152 REM                                wird OUT NICHT aufgerufen - das
30153 REM                                Programm endet mit END und der
30154 REM                                BBC-BASIC-Prompt bleibt offen.
30155 REM                                (fuer interaktives Debuggen;
30156 REM                                 `uv run tools/run.py --hold`
30157 REM                                 setzt die Variable automatisch.)
30160 REM   FN_dbg_time                  Centisekunden seit Init
30170 REM
30180 REM Auf echter Hardware haben die Ports &00/&10/&20 keine Funktion
30190 REM (im eZ80F92 unbelegt) - Code bleibt kompatibel, aber ohne
30200 REM Debugger-Effekt.
30205 REM
30206 REM Hintergrund:
30207 REM   Debug-I/O-Ports       https://github.com/tomm/fab-agon-emulator#debug-io-space
30208 REM   MOS-API (RST 08h)     https://agonplatform.github.io/agon-docs/mos/API/
30209 REM   System Variables      https://agonplatform.github.io/agon-docs/mos/System-Variables/
30210 REM ===============================================================
30220 :
30230 DEF PROC_dbg_init(log$)
30240   LOCAL h%
30250   dbg_log% = 0
30260   dbg_start% = TIME
30270   IF LEN(log$) > 0 THEN h% = OPENOUT log$ : IF h% <> 0 THEN dbg_log% = h%
30280   PROC_dbg_asm
30290   PRINT "[dbg] init t=0 log=";
30300   IF dbg_log% <> 0 THEN PRINT log$ ELSE PRINT "-"
30310 ENDPROC
30320 :
30330 DEF PROC_dbg_close
30340   IF dbg_log% <> 0 THEN CLOSE #dbg_log% : dbg_log% = 0
30350 ENDPROC
30360 :
30370 DEF PROC_dbg_asm
30380   REM Legt 15 Bytes inline-Asm an: je 5 Byte fuer bp/regs/exit.
30390   REM Layout (offsets aus dbg_code%):
30400   REM   0: LD A,n  D3 10  RET         (bp)
30410   REM   5: LD A,n  D3 20  RET         (regs)
30420   REM  10: LD A,n  D3 00  RET         (exit)
30430   DIM dbg_code% 30
30440   FOR pass% = 0 TO 3 STEP 3
30450     P% = dbg_code%
30460     [
30470     OPT pass%
30480     LD A, 0
30490     OUT (&10), A
30500     RET
30510     LD A, 0
30520     OUT (&20), A
30530     RET
30540     LD A, 0
30550     OUT (&00), A
30560     RET
30570     ]
30580   NEXT pass%
30590   dbg_bp% = dbg_code%
30600   dbg_regs% = dbg_code% + 5
30610   dbg_exit% = dbg_code% + 10
30620 ENDPROC
30630 :
30640 DEF FN_dbg_time = (TIME - dbg_start%)
30650 :
30660 DEF PROC_dbg_log(msg$)
30670   LOCAL t%, line$
30680   t% = TIME - dbg_start%
30690   line$ = "[dbg t=" + STR$(t%) + "] " + msg$
30700   PRINT line$
30710   IF dbg_log% <> 0 THEN PRINT #dbg_log%, line$
30720 ENDPROC
30730 :
30740 DEF PROC_dbg_trace(lbl$, val)
30750   LOCAL msg$
30760   msg$ = lbl$ + " = " + STR$(val)
30770   PROC_dbg_log(msg$)
30780 ENDPROC
30790 :
30800 DEF PROC_dbg_assert(cond, msg$)
30810   IF cond THEN ENDPROC
30820   PROC_dbg_log("ASSERT FAIL: " + msg$)
30830   PRINT "=== TEST FAIL ==="
30840   PROC_dbg_exit(1)
30845 ENDPROC
30850 :
30860 DEF PROC_dbg_bp(id%)
30870   REM Patcht die LD A,n Konstante und ruft dann das Snippet auf.
30880   IF dbg_bp% = 0 THEN PROC_dbg_asm
30890   ?(dbg_bp% + 1) = id% AND &FF
30900   PROC_dbg_log("breakpoint id=" + STR$(id%))
30910   CALL dbg_bp%
30920 ENDPROC
30930 :
30940 DEF PROC_dbg_regs(id%)
30950   IF dbg_regs% = 0 THEN PROC_dbg_asm
30960   ?(dbg_regs% + 1) = id% AND &FF
30970   PROC_dbg_log("regs dump id=" + STR$(id%))
30980   CALL dbg_regs%
30990 ENDPROC
31000 :
31010 DEF PROC_dbg_exit(code%)
31012   dbg_hold% = 0 : REM HOLD-MARKER: --hold ersetzt "= 0" durch "= TRUE"
31015   IF dbg_hold% = 0 THEN 31020
31016   PROC_dbg_log("exit deferred (hold) code=" + STR$(code%))
31017   END
31020   IF dbg_exit% = 0 THEN PROC_dbg_asm
31030   ?(dbg_exit% + 1) = code% AND &FF
31040   PROC_dbg_log("exit code=" + STR$(code%))
31050   PROC_dbg_close
31060   CALL dbg_exit%
31070   REM Fallback: wenn OUT (&00),A keine Wirkung hat (echte Hardware),
31080   REM beenden wir das BASIC-Programm ueber END:
31090 END
