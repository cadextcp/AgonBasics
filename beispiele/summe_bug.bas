10 REM summe_bug.bas - Teaching-Example fuer docs/DEBUGGING.md
15 REM Absichtlich verbuggt: berechnet Fakultaet 1..5 (sollte 120),
16 REM liefert aber 0. Die PROC_dbg_trace-Ausgaben zeigen warum.
17 REM Uebung: spotten, fixen (Tipp: Initialisierung in Zeile 30).
20 REM USES lib/debug
25 PROC_dbg_init("")
30 f% = 0
35 PROC_dbg_trace("f% nach Init", f%)
40 FOR i% = 1 TO 5
45   PROC_dbg_trace("f% vor *", f%)
50   f% = f% * i%
55   PROC_dbg_trace("f% nach *", f%)
60 NEXT
65 PROC_dbg_assert(f% = 120, "5! soll 120 sein")
70 PRINT "5! = "; STR$(f%)
80 END
