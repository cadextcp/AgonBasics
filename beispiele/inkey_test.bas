10 REM inkey_test.bas - prueft INKEY(-N) Syntax in Agon BBC BASIC
20 REM USES lib/debug
30 PROC_dbg_init("")
40 PROC_dbg_log("teste INKEY(-66) [A-Taste per FabGL-vkey]")
50 a% = INKEY(-66)
60 PROC_dbg_trace("INKEY(-66)", a%)
70 PROC_dbg_log("teste INKEY(-50) [D-Taste]")
80 d% = INKEY(-50)
90 PROC_dbg_trace("INKEY(-50)", d%)
100 PROC_dbg_log("teste INKEY(-99) [SPACE BBC Micro code]")
110 s% = INKEY(-99)
120 PROC_dbg_trace("INKEY(-99)", s%)
130 PROC_dbg_log("alle INKEY(-N) Syntaxtests durchgelaufen")
140 PRINT "=== TEST PASS ==="
150 PROC_dbg_exit(0)
160 END
