# Iteration 01 — Paddle zeichnen und bewegen

## Lernziel

Nach dieser Iteration verstehst du:

1. **Wie ein Grafikmodus gesetzt wird.** `MODE 8` gibt dir 320×240 Pixel
   mit 64 Farben; die logische Koordinaten-Flaeche ist aber 1280×1024 —
   fuer Grafik-Befehle rechnest du immer in logischen Koordinaten.
2. **Wie ein gefuelltes Rechteck entsteht.** `MOVE` + `PLOT 101` ist das
   Agon-Pendant zu "Rechteck mit Fuellfarbe". Die Farbe setzt `GCOL`
   vorher.
3. **Wie Tastatur-Input ohne Blockieren abgefragt wird.** `INKEY(-N)`
   prueft einen bestimmten Scan-Code *direkt* (TRUE/FALSE); `INKEY(0)`
   holt sich das naechste ASCII-Zeichen aus dem Puffer (oder -1 wenn
   nichts da ist).
4. **Wie ein Game-Loop aufgebaut ist.** `REPEAT ... UNTIL quit%` ruft
   jede Frame `PROC_tick` auf, und `*FX 19` wartet darin auf VSync —
   dadurch laeuft der Loop auf genau 60 Hz.
5. **Wie man "nur den veraenderten Teil" neu zeichnet.** Statt den
   gesamten Bildschirm mit `CLG` zu loeschen, uebermalt `PROC_redraw`
   nur die alte Paddle-Position schwarz und zeichnet an der neuen
   Position weiss. Das ist flicker-frei und spart Rechenzeit.

## Steuerung

| Taste | Aktion                    |
|-------|---------------------------|
| **A** | Paddle nach links bewegen |
| **D** | Paddle nach rechts        |
| **ESC** | Programm beenden        |

## Koordinaten-System

Wichtig fuer alle Grafik-Befehle: Agon BBC BASIC uebernimmt das
klassische BBC-Micro-Schema — der **Ursprung (0, 0) ist links-UNTEN**,
`Y` waechst nach oben.

Deshalb sagt im Code `padY% = 80`:

> "das Paddle sitzt 80 Pixel *ueber* dem unteren Rand"

Auf einem 1280×1024-Logikschirm ist das also *weit unten*, wo man das
Paddle erwartet.

## Code-Gliederung

```
Zeile 10-30   Header-REMs + REM USES lib/debug
Zeile 40-90   MODE 8, Cursor aus, Keyboard-Repeat
Zeile 100-199 Konstanten (Bildschirm, Paddle, Geschwindigkeit)
Zeile 200-290 Start-Position und quit%-Flag
Zeile 300-399 Initialzeichnung: schwarzer Bg, weisses Paddle
Zeile 400-499 Haupt-Loop (REPEAT PROC_tick UNTIL quit%)
Zeile 500-599 Aufraeumen + sauberer Exit via PROC_dbg_exit(0)
Zeile 600-699 PROC_fill_rect - Rechteck in aktueller GCOL zeichnen
Zeile 700-799 PROC_tick - ein Frame (Input + Move + Clip + Redraw)
Zeile 800-899 PROC_redraw - altes Paddle schwarz, neues weiss
```

## Detail-Kommentar zum Code

### `MODE 8` + Cursor aus + Keyboard-Repeat

```
50 MODE 8
70 VDU 23, 1, 0
130 *FX 11, 250
140 *FX 12, 33
```

- `MODE 8` schaltet in den Grafikmodus. Danach ist der Schirm schwarz
  und `CLG` sowie `GCOL`/`PLOT` arbeiten auf dem Grafikbuffer.
- `VDU 23, 1, 0` blendet den blinkenden Text-Cursor aus (`1` fuer
  *setze Cursor-Status*, `0` fuer *unsichtbar*).
- `*FX 11, 250` und `*FX 12, 33` setzen Repeat-Delay und Repeat-Rate
  der Tastatur. Default ist "langsam" — mit 250×10 ms = 2.5 s Delay
  und 33×10 ms = 0.33 s Pause zwischen Wiederholungen laeuft das
  Gedrueckthalten von A/D gerade so, dass INKEY(-N) auf jedes Frame
  reagiert.

### Der Game-Loop

```
400 REPEAT
410   PROC_tick
420 UNTIL quit%
```

`PROC_tick` ist die **gesamte Frame-Logik**: Input lesen, Paddle
bewegen, Clipping, Redraw, VSync. Die Schleife laeuft so lange, bis
`quit%` auf `TRUE` gesetzt wurde (das passiert in `PROC_tick`, wenn
`ESC` gedrueckt wird).

### `PROC_tick` im Detail

```
700   oldX% = padX%
720   k% = INKEY(0)
730   IF k% = 27 THEN quit% = TRUE
780   IF INKEY(-66) THEN padX% = padX% - padSpd%
790   IF INKEY(-51) THEN padX% = padX% + padSpd%
820   IF padX% < 0 THEN padX% = 0
830   IF padX% + padW% > scrW% THEN padX% = scrW% - padW%
860   IF padX% <> oldX% THEN PROC_redraw(oldX%)
900   *FX 19
```

1. **Alte Position merken** (`oldX%`). Brauchen wir, um das Paddle an
   der Vorgaenger-Stelle wieder ueberzumalen.
2. **Escape pruefen.** `INKEY(0)` holt sich das naechste Zeichen aus
   dem Puffer (oder -1). ASCII 27 ist ESC.
3. **A/D pruefen.** `INKEY(-66)` bedeutet "ist *momentan* die Taste
   mit Scancode 66 (=A) gedrueckt?". Selbiges fuer `-51` (=D).
   **Scancode-Liste:** siehe `docs/REFERENCE.md#tastatur`.
4. **Clipping.** Paddle darf nicht links/rechts aus dem Bild laufen.
5. **Neu zeichnen** — aber nur wenn sich `padX%` wirklich veraendert
   hat. So vermeiden wir unnoetiges Flackern.
6. **VSync.** `*FX 19` wartet auf das naechste Vertikal-Retrace
   (~16.67 ms). Damit laeuft der Loop genau 1x pro Frame, ohne die
   CPU zu ueberlasten.

### `PROC_redraw`

```
960   GCOL 0, 0                                 : REM Farbe 0 = schwarz
970   PROC_fill_rect(oldX%, padY%, padW%, padH%): REM altes weg
1000  GCOL 0, 7                                 : REM Farbe 7 = weiss
1010  PROC_fill_rect(padX%, padY%, padW%, padH%): REM neues hin
```

Zwei Rechtecke: eines in Hintergrundfarbe ueber der alten Position
(loescht das Paddle dort) und eines in Vordergrundfarbe an der neuen
Position.

**Warum nicht einfach `CLG` + neu zeichnen?** Weil `CLG` den ganzen
Schirm fuer einen kurzen Moment schwarz macht, bis das neue Paddle
gezeichnet ist. Bei 60 Hz sieht man das als Flackern.

## Ausblick

In **Iteration 02** kommen `ballX%`, `ballY%`, `ballDX%`, `ballDY%` dazu,
plus eine `PROC_ball_move`, die jeden Tick aufgerufen wird und den Ball
an Waenden abprallen laesst. Die Paddle-Logik aus Iteration 01 bleibt
1:1 gleich.
