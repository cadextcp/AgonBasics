10 REM Demonstriert die Nutzung von lib/debug.bas.
20 REM Der Marker in Zeile 30 sorgt dafuer, dass deploy.py
30 REM USES lib/debug
40 REM die Library beim Stagen automatisch ans Ende anhaengt.
50 :
60 PROC_dbg_init("")
70 PROC_dbg_log("demo startet")
80 :
90 REM Traceausgaben fuer Variablen
100 x% = 42
110 PROC_dbg_trace("x%", x%)
120 FOR i% = 0 TO 4
130   y% = i% * i%
140   PROC_dbg_trace("y% (iter " + STR$(i%) + ")", y%)
150 NEXT i%
160 :
170 REM Assertion-Beispiel: diese hier passt
180 PROC_dbg_assert(x% = 42, "x% sollte 42 sein")
190 :
200 REM Emulator-Breakpoint (im Emulator mit -d startet hier der Debugger)
210 REM Ohne -d: kein Effekt, Programm laeuft weiter
220 PROC_dbg_bp(1)
230 :
240 REM CPU-Zustand dumpen (nur im Emulator mit -d)
250 PROC_dbg_regs(1)
260 :
270 PROC_dbg_log("demo fertig")
280 PRINT "=== TEST PASS ==="
290 PROC_dbg_exit(0)
300 :
310 REM Ab hier wird lib/debug.bas von deploy.py angehaengt.
320 END
