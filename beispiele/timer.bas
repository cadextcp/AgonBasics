10 REM === 20-Minuten Countdown Timer ===
20 MODE 8 : VDU 23, 1, 0
30 DIM c%(11)
40 c%(0)=48:c%(1)=52:c%(2)=56:c%(3)=60
50 c%(4)=44:c%(5)=12:c%(6)=15:c%(7)=11
60 c%(8)=3:c%(9)=19:c%(10)=35:c%(11)=51
70 total%=1200 : start%=TIME
80 COLOUR 128+0 : CLS
90 REPEAT
100   now%=TIME
110   el%=(now%-start%) DIV 100
120   IF el%>total% el%=total%
130   re%=total%-el%
140   m%=re% DIV 60 : s%=re% MOD 60
150   o%=(now% DIV 15) MOD 12
160   REM --- Raender ---
170   FOR i%=0 TO 39
180     COLOUR c%((o%+i%) MOD 12)
190     PRINT TAB(i%,1);"=";
200     PRINT TAB(i%,27);"=";
210   NEXT
220   REM --- Titel ---
230   ti$="COUNTDOWN"
240   FOR i%=0 TO 8
250     COLOUR c%((o%+i%) MOD 12)
260     PRINT TAB(15+i%,4);MID$(ti$,i%+1,1);
270   NEXT
280   REM --- Timer ---
290   t$=CHR$(48+m% DIV 10)+CHR$(48+m% MOD 10)+":"+CHR$(48+s% DIV 10)+CHR$(48+s% MOD 10)
300   FOR i%=0 TO 4
310     COLOUR c%((o%+i%*2) MOD 12)
320     PRINT TAB(15+i%*2,12);MID$(t$,i%+1,1);
330   NEXT
340   REM --- Restzeit ---
350   COLOUR c%((o%+3) MOD 12)
360   IF m%>0 THEN PRINT TAB(11,17);m%;" Min ";s%;" Sek    "; ELSE PRINT TAB(11,17);s%;" Sekunden      ";
370   REM --- Fortschrittsbalken ---
380   bw%=30 : bf%=bw%*re% DIV total%
390   pc%=re%*100 DIV total%
400   COLOUR c%((o%+5) MOD 12)
410   PRINT TAB(4,22);"[";
420   FOR i%=0 TO bw%-1
430     IF i%<bf% THEN COLOUR 128+c%((o%+i%) MOD 12):PRINT " "; ELSE COLOUR 128+0:PRINT " ";
440   NEXT
450   COLOUR 128+0
460   COLOUR c%((o%+5) MOD 12)
470   PRINT "] ";pc%;"% ";
480   REM --- Warten ---
490   w%=now%+8:REPEAT UNTIL TIME>=w%
500 UNTIL re%<=0
510 REM --- FERTIG! ---
520 SOUND 0,-10,100,20
530 FOR j%=0 TO 19
540   COLOUR c%(j% MOD 12)
550   PRINT TAB(13,12);"  FERTIG!  ";
560   w%=TIME+25:REPEAT UNTIL TIME>=w%
570   COLOUR 0
580   PRINT TAB(13,12);"           ";
590   w%=TIME+25:REPEAT UNTIL TIME>=w%
600 NEXT
610 VDU 23,1,1 : MODE 0
