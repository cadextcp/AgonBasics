10 REM test_schleife.bas - FOR/NEXT Summe 1..10
20 REM USES lib/debug
30 :
40 PROC_dbg_init("")
50 summe% = 0
60 FOR i% = 1 TO 10
70   summe% = summe% + i%
80 NEXT i%
90 :
100 PROC_dbg_assert(summe% = 55, "Summe 1..10 muss 55 sein")
110 :
120 PRINT "=== OUTPUT BEGIN ==="
130 PRINT "Summe 1..10 = "; STR$(summe%)
140 PRINT "=== OUTPUT END ==="
150 :
160 PRINT "=== TEST PASS ==="
170 PROC_dbg_exit(0)
180 END
