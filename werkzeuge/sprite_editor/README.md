# SPED — Sprite-Editor

`sped.bas` ist ein kompletter Sprite-Editor, der direkt auf dem Agon
laeuft. Man kann damit 16x16- oder 8x8-Sprites pixelweise zeichnen, als
Animation abspielen und in verschiedene Formate exportieren (raw RGB,
RGBA, BASIC-DATA-Statements).

**Autor:** [robogeek42](https://github.com/robogeek42/agon_sped) — wir
verwenden Version v1.07, MIT-lizenziert. Details und Update-Workflow in
[`UPSTREAM.md`](UPSTREAM.md).

## Start

Einmal deployen, dann starten:

```
uv run tools/deploy.py
uv run tools/sped.py
```

Der Wrapper startet den GUI-Emulator mit Console8-MOS (VDP 2.0+ wird
fuer Bitmap-Sprites gebraucht) und laedt `sped.bas` automatisch.

Alternativ:

```
uv run tools/run.py --program sped.bas
```

## Voraussetzungen

- Console8-Firmware (Default in AgonBasics): MOS 2.3.3 mit VDP 2.x.
  Quark (MOS 1.04) geht nicht — Bitmap-backed Sprites fehlen dort.
- MODE 8 (64 Farben, 320x240).

## Tastaturbelegung (Kurzfassung)

Im Editor:

| Taste             | Aktion                                           |
|-------------------|--------------------------------------------------|
| Pfeile            | Cursor im Pixelraster bewegen                    |
| WASD              | Palettenfarbe waehlen (Up/Down/Left/Right)       |
| Space / Enter     | Pixel auf aktuelle Farbe setzen                  |
| Backspace         | Pixel loeschen (Farbe 0)                         |
| P                 | Farbe unter Cursor "picken"                      |
| F                 | Grid / Block mit aktueller Farbe fuellen         |
| C                 | Grid / Block loeschen                            |
| B                 | Block-Auswahl starten / abschliessen             |
| `-` / `=`         | Block kopieren / einfuegen                       |
| `#` / `~`         | Block spiegeln (horizontal / vertikal)           |
| `[` / `]`         | Block rotieren (links / rechts)                  |
| `/`               | Flood-Fill ab Cursor                             |
| U                 | Undo (eine Ebene)                                |
| `,` / `.`         | vorheriges / naechstes Bitmap                    |
| G                 | gezieltes Bitmap per Nummer anspringen           |
| M                 | Anzahl Frames setzen                             |
| Y                 | Loop-Typ (Left-Right / Ping-Pong) umschalten     |
| R                 | Loop-Geschwindigkeit setzen                      |
| K                 | Shortcut-Taste fuer Farbe festlegen (1-9)        |
| T                 | Transparenzfarbe setzen                          |
| I                 | Sticky-Mode (malen ohne Space)                   |
| N                 | Farbe X im Bild durch Farbe Y ersetzen           |
| L / V             | Laden / Speichern                                |
| E                 | Exportieren (diverse Formate)                    |
| X                 | Editor beenden (mit Bestaetigung)                |

Volle Liste + Screenshot:
<https://github.com/robogeek42/agon_sped#readme>.

## Dateien

| Datei          | Zweck                                            |
|----------------|--------------------------------------------------|
| `sped.bas`     | der Editor selbst (BBC BASIC, ~1100 Zeilen)     |
| `sped.ini`     | Konfiguration (Bitmap-Groesse, Joystick, etc.)  |
| `LICENSE`      | Original-MIT-License, Copyright 2023 robogeek42 |
| `UPSTREAM.md`  | Herkunft, Update-Workflow, Delta zum Upstream   |

`sped.ini` wird beim Start gelesen. Darin einstellbar:

- `SIZE=1` (16x16) oder `SIZE=2` (8x8)
- `JOY=1` aktiviert Joystick-Input (sonst nur Tastatur)
- `BM_MAX=48` maximale Anzahl Bitmaps (24 bei 16x16, 48 bei 8x8)
- `CWRAP=1` Cursor-Wraparound am Rand
- `C1=21 / C2=19` Hilfs-Text-Farben

## Dateiformate

Der Editor speichert und exportiert:

- **RGB888** — 3 Bytes pro Pixel (R/G/B)
- **RGBA8888** — 4 Bytes pro Pixel (R/G/B/A)
- **RGBA2222** — 1 Byte pro Pixel (2-bit pro Kanal)
- **DATA-Statements** — als BBC-BASIC-`DATA`-Zeilen (per "Export")

Die Endungen sind in `sped.ini` konfigurierbar.
