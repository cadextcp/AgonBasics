# AgonBasics Schulung — Breakout in Iterationen

Dieser Ordner zerlegt das `beispiele/breakout.bas` Spiel in einzelne
Lern-Iterationen. Jede Iteration fuegt **genau einen** Aspekt hinzu, sodass
man sich auf ein Konzept konzentrieren kann.

## Lernpfad

| #  | Datei                  | Was dazukommt                          |
|----|------------------------|----------------------------------------|
| 01 | `01_paddle.bas`        | MODE 8, Game-Loop, Paddle-Bewegung     |
| 02 | `02_paddle_sprite.bas` | Paddle als Bitmap-Sprite statt PLOT-Rechteck (VDU 23,27, sped-Asset) |
| 03 | (kommt spaeter)        | Ball bewegen und an Waenden abprallen  |
| 04 | (kommt spaeter)        | Paddle-Ball-Kollision                  |
| 05 | (kommt spaeter)        | Ziegel-Array + Kollision               |
| 06 | (kommt spaeter)        | Punkte, Leben, Game-Over               |

## Aufruf

Einmalig deployen, damit die SD-Karte die Schulungs-BAS-Dateien kennt:

```
uv run tools/deploy.py
```

Dann eine Iteration interaktiv starten:

```
uv run tools/run.py --program 01_paddle.bas
uv run tools/run.py --program 02_paddle_sprite.bas
```

Iteration 02 braucht zusaetzlich die Asset-Datei
`schulung/02_paddle.rgba` (mit `tools/sped.py` erstellt; Details in
[`02_paddle_sprite.md`](02_paddle_sprite.md)).

## Design-Entscheidungen

- Jede Iteration ist eine **eigene, selbststaendig lauffaehige Datei**.
  Keine Abhaengigkeiten zwischen den Iterationen.
- Zeilennummern-Bereiche immer gleich strukturiert:
  - 10-99: Header, MODE, Init
  - 100-299: Konstanten
  - 300-399: Initialzeichnung
  - 400-499: Haupt-Loop (`REPEAT ... UNTIL`)
  - 500+: Prozeduren
- Alle PROC-Bodys und FOR-Schleifen sind mit **2 Spaces pro
  Schachtelungs-Ebene** eingerueckt.
- `REM USES lib/debug` aktiviert `PROC_dbg_init`/`PROC_dbg_exit`, damit
  der Emulator sich nach `ESC` sauber beendet (`tools/deploy.py`
  inlined die Library beim Deploy automatisch).
- Jede Iteration hat eine **dazugehoerige `.md`**, die das Konzept
  erklaert, Scancodes auflistet und den Code abschnittsweise kommentiert.

## Tastatur

Default ist `SET KEYBOARD 2` (Deutsch). Bei der Paddle-Bewegung nutzen
wir **A** (links) und **D** (rechts), weil das auf jedem Layout an
derselben physischen Position bleibt. `ESC` beendet das Programm.

Hintergrund zu `INKEY(-N)` steht in `../docs/REFERENCE.md#tastatur`.

## Siehe auch

- [`01_paddle.md`](01_paddle.md) - detaillierte Erklaerung zu Iteration 01
- [`02_paddle_sprite.md`](02_paddle_sprite.md) - Iteration 02 (Sprite-API, sped-Asset)
- [`../beispiele/breakout.bas`](../beispiele/breakout.bas) - das fertige Spiel
- [`../beispiele/sprite.bas`](../beispiele/sprite.bas) - Referenz-Beispiel fuer Bitmap-Sprites
- [`../docs/REFERENCE.md`](../docs/REFERENCE.md) - Spickzettel (VDU/PLOT/Scancodes)
