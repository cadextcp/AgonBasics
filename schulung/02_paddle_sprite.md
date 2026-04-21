# Iteration 02 — Paddle als Bitmap-Sprite

## Lernziel

Nach dieser Iteration verstehst du:

1. **Dass der Agon-VDP eine eigene Bitmap- und Sprite-API hat**, die
   unabhaengig von `PLOT`-Kommandos arbeitet. Bitmaps werden einmal in
   einen Buffer geladen; Sprites sind "Kopien" des Bitmaps, die per
   VDU-Kommando bewegt werden. Vollstaendige Spezifikation:
   <https://agonplatform.github.io/agon-docs/vdp/Bitmaps-API/>.
2. **Den Unterschied zwischen physischen und logischen Koordinaten.**
   Iteration 01 hat `MOVE`/`PLOT` in **logischen** Koordinaten
   (1280×1024) gesetzt. Die Sprite-API dagegen arbeitet in
   **physischen** Pixeln — in `MODE 8` also `x ∈ [0..319]`,
   `y ∈ [0..239]`. Deshalb sind die Konstanten hier kleiner und
   `padSpd%` ist nur noch `2` statt `40`.
3. **Wie man ein Asset aus sped (oder einem anderen Tool) laedt.**
   Die Datei `02_paddle.rgba` ist 1024 Bytes: 16 × 16 Pixel × 4 Bytes
   pro Pixel (RGBA8888). Man liest sie per `OPENIN` / `BGET#` und
   uebergibt die Bytes unveraendert ans VDU-Kommando.
4. **Wie man eine Loop ohne `CLG`/Redraw baut.** Der VDP merkt sich
   die Sprite-Position und zeichnet den Hintergrund bei einer
   Positions-Aenderung selbst wieder frei. Kein "altes Paddle
   schwarz uebermalen" mehr noetig — `PROC_redraw` aus Iteration 01
   entfaellt komplett.

## Voraussetzung: das Sprite-Asset

Du brauchst eine Datei `02_paddle.rgba` (16×16 RGBA8888, 1024 Bytes)
im Schulungs-Ordner. Erstellen:

```
uv run tools/sped.py
```

Im Editor:

1. Paddle pixelweise malen (Pfeiltasten + Space, oder `I`-Sticky).
2. `V` (saVe) druecken → Dateinamen eingeben (z. B. `paddle`).
3. `Format 1)RGB8 2)RGBA8 3)RGBA2` → **`2`** waehlen (RGBA8888 =
   das Format, das die VDU-API erwartet). Ohne die `2` landet man
   bei RGB888 (3 Bytes/Pixel, passt nicht).
4. sped schreibt ins Arbeitsverzeichnis des Emulators. Die Datei
   liegt danach unter:
   `sdcard/staged/beispiele/sprite_editor/paddle`  *(ohne Endung!)*
5. Ins Repo holen und umbenennen:
   ```
   cp sdcard/staged/beispiele/sprite_editor/paddle schulung/02_paddle.rgba
   ```
6. Pruefen: `ls -la schulung/02_paddle.rgba` sollte `1024` Bytes
   anzeigen.

Beim naechsten `uv run tools/deploy.py` wird die Datei automatisch
nach `sdcard/staged/beispiele/02_paddle.rgba` gesynct.

## Steuerung

| Taste   | Aktion                    |
|---------|---------------------------|
| **A**   | Paddle nach links         |
| **D**   | Paddle nach rechts        |
| **ESC** | Programm beenden          |

## Die Sprite-API in einer Nussschale

Alle Sprite-Kommandos gehen ueber `VDU 23, 27, <command>, <args>`.
Die wichtigsten fuer diese Iteration:

| Kommando                    | Bedeutung                                  |
|-----------------------------|--------------------------------------------|
| `VDU 23, 27, 0, n`          | Bitmap `n` als aktiv waehlen               |
| `VDU 23, 27, 1, w; h; data` | Bytes ins aktive Bitmap schreiben (RGBA8888) |
| `VDU 23, 27, 4, n`          | Sprite `n` als aktiv waehlen               |
| `VDU 23, 27, 5`             | Frames des aktiven Sprites loeschen        |
| `VDU 23, 27, 6, b`          | Bitmap `b` als Frame anhaengen             |
| `VDU 23, 27, 7, N`          | Anzahl aktiver Sprites setzen              |
| `VDU 23, 27, 11`            | aktives Sprite einblenden                  |
| `VDU 23, 27, 12`            | aktives Sprite ausblenden                  |
| `VDU 23, 27, 13, x; y;`     | aktives Sprite auf (x,y) positionieren     |
| `VDU 23, 27, 15`            | Refresh — alle Sprite-Aenderungen sichtbar |

Wichtig: **nach jeder Aenderung** an einem Sprite braucht es ein
`VDU 23, 27, 15`, sonst sieht man nichts — der VDP sammelt die
Kommandos und zeigt sie erst nach dem Refresh an.

## Code-Gliederung

```
Zeile 10-30    Header + USES lib/debug
Zeile 40-100   MODE 8 + Cursor aus + Keyboard-Repeat
Zeile 120-270  Bitmap 0 mit 02_paddle.rgba befuellen
Zeile 290-400  Sprite 0 an Bitmap 0 koppeln und aktivieren
Zeile 420-500  Konstanten in PHYSISCHEN Pixeln (!)
Zeile 520-560  Sprite initial positionieren + Refresh
Zeile 580-620  Haupt-Loop (REPEAT PROC_tick UNTIL quit%)
Zeile 640-720  Aufraeumen + Exit
Zeile 770-990  PROC_tick: Input lesen, Paddle bewegen, Sprite
               verschieben, Refresh, VSync
```

## Was gegenueber Iteration 01 weggefallen ist

- `GCOL`, `CLG`, `MOVE`, `PLOT 101` — kommen nicht mehr vor. Alles
  Zeichnen erledigt der VDP via Sprite-API.
- `PROC_fill_rect` und `PROC_redraw` aus Iteration 01 gibt es hier
  nicht mehr. Das Sprite ist "selbstzeichnend".
- Kein `oldX%` / "altes Paddle wegloeschen". Der VDP merkt sich die
  vorige Sprite-Position und stellt den Hintergrund wieder her.

## Was NEU hinzugekommen ist

- `OPENIN` + `BGET#` + `CLOSE#` zum Einlesen einer Binaerdatei.
- Die `VDU 23, 27, ...`-Befehlsfamilie.
- Zwei Koordinaten-Welten nebeneinander: fuer `MODE 8` sind es
  physisch 320×240, waehrend `MOVE`/`PLOT` weiterhin in logisch
  1280×1024 rechnen wuerden (wir benutzen die hier aber nicht).

## Ausblick

Iteration 03 koennte sein:

- **Ball als Sprite** — mit einem zweiten Bitmap (z. B. `02_ball.rgba`,
  8×8 oder 16×16) und einem zweiten Sprite. Dann `VDU 23, 27, 7, 2`
  fuer "2 aktive Sprites".
- **Animierter Paddle** — mehrere Frames in ein Sprite, Frames per
  `VDU 23, 27, 6, n` anhaengen und per `VDU 23, 27, 10` cyclen.
