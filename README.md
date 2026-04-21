# AgonBasics

Basisprojekt fuer BBC-BASIC-Entwicklung auf dem [Agon Light /
Console8](https://www.thebyteattic.com/p/agon.html). Clonen, Setup
ausfuehren, loslegen - inklusive Emulator, Popup-MOS-SD-Karte,
Debug-Library, Headless-Testrunner und GitHub-Actions-CI.

## Schnellstart

```
git clone https://github.com/cadextcp/AgonBasics.git
cd AgonBasics

# Emulator und SD-Karte einrichten (~8 MB Download)
uv run tools/setup.py

# Ein Beispiel ausfuehren (laedt und startet automatisch)
uv run tools/run.py --program hello.bas

# Headless / scriptbar
uv run tools/run.py --headless --program hello.bas

# Tests
uv run tools/test.py
```

Fuer die Installation von `uv` und alles weitere siehe
[docs/SETUP.md](docs/SETUP.md).

## Was ist enthalten?

| Ordner | Inhalt |
|---|---|
| `beispiele/` | BBC-BASIC-Beispielprogramme (`hello`, `sprite`, `timer`, `assembler`, `melodie`, `debug_demo`, ...) |
| `lib/` | `debug.bas` - Trace-/Assert-/Breakpoint-Library (funktioniert Emulator UND Hardware) |
| `schulung/` | Lerngruppen-Iterationen (Breakout schrittweise aufgebaut, jede Iteration selbststaendig) |
| `werkzeuge/` | Agon-seitige BASIC-Werkzeuge: `sprite_editor/sped.bas` (von robogeek42, MIT) |
| `tests/` | `test_*.bas` + erwartete Ausgaben fuer `tools/test.py` |
| `tools/` | Python-Skripte: `setup`, `deploy`, `run`, `debug`, `test`, `deploy_sdcard`, `make_ship`, `install_vscode_extension`, `sped` |
| `tools/vscode-bbcbasic/` | Lokale VS-Code-Extension: Syntax-Highlighting fuer `.bas` (REM, Keywords, Strings) |
| `docs/` | Deutsche Dokumentation: Setup, Workflow, Debugging, Testing, Resources |
| `.vscode/` | VS-Code-Tasks und -Launch-Configs |
| `.github/workflows/` | CI-Workflow (Headless-Tests auf Windows-Runner) |

## Beispiele

| Datei | Beschreibung |
|---|---|
| `hello.bas` | Hello World |
| `eingabe.bas` | Tastatureingabe und `INKEY` |
| `schleife.bas` | `FOR`/`NEXT`-Schleife |
| `dreieck.bas` | Gefuelltes Dreieck (`PLOT`) |
| `rechteck.bas` | Rechteck zeichnen (`DRAW`) |
| `kreis.bas` | Kreis zeichnen (`PLOT`) |
| `prozedur.bas` | `DEF PROC` Prozeduren |
| `melodie.bas` | Melodie mit `SOUND`/`DATA` |
| `datei.bas` | Datei-Operationen (`OPENOUT`/`CLOSE#`) |
| `assembler.bas` | Inline-eZ80-Assembler |
| `sprite.bas` | Hardware-Sprite laden und mit WASD bewegen |
| `timer.bas` | 20-Minuten-Countdown mit Regenbogen-Animation |
| `debug_demo.bas` | Demonstriert `lib/debug.bas` (PROC_dbg_trace, _bp, _exit) |
| `summe_bug.bas` | Intentional-buggy Fakultaet - fuer die Debug-Uebung aus docs/DEBUGGING.md |
| `breakout.bas` | Einfaches Breakout-Spiel (MODE 8, A/D bewegt Paddle, ESC beendet) |
| `breakout_smoke.bas` | Syntax-Smoke-Test fuer breakout - ruft alle PROCs ohne MODE, fuer headless-Debug |

## Tooling

| Befehl | Zweck |
|---|---|
| `uv run tools/setup.py` | Einmalig: Emulator laden, SD-Karte vorbereiten |
| `uv run tools/deploy.py` | `beispiele/` + `lib/` -> `sdcard/staged/beispiele/` |
| `uv run tools/run.py [--headless] [--program X.bas]` | Emulator starten (GUI oder CLI) |
| `uv run tools/debug.py [--program X.bas] [-b 0xADDR]` | GUI-Emulator mit eZ80-Debugger |
| `uv run tools/test.py` | Headless-Tests aus `tests/` |
| `uv run tools/deploy_sdcard.py F: --confirm` | Auf echte microSD kopieren |
| `uv run tools/make_ship.py` | Beispiel-Asset (16x16 Sprite) erzeugen |
| `uv run tools/fetch_docs.py` | Offizielle Agon-Doku lokal spiegeln |
| `uv run tools/install_vscode_extension.py` | BBC-BASIC-Syntax-Highlighting in VS Code aktivieren |
| `uv run tools/sped.py` | Sprite-Editor SPED starten (deployt + oeffnet den Editor) |

## Sprite-Editor SPED

`werkzeuge/sprite_editor/sped.bas` ist ein vollwertiger Bitmap-Sprite-Editor
fuer den Agon, uebernommen von [robogeek42/agon_sped](https://github.com/robogeek42/agon_sped)
(MIT-lizenziert). Unterstuetzt 8x8 oder 16x16 Sprites, bis zu 24/48 Frames
als Animation, Export als RGB888/RGBA8888/RGBA2222 oder BBC-BASIC-DATA-
Zeilen. Start:

```
uv run tools/sped.py
```

Details + Tastaturbelegung: [`werkzeuge/sprite_editor/README.md`](werkzeuge/sprite_editor/README.md).

## VS Code / Syntax-Highlighting

`.bas` ist als BBC-BASIC-Sprache registriert. Die aktuelle VS-Code-VB-
Grammatik erkennt `REM`-Kommentare leider nicht (sie kennt nur `'`), darum
liegt unter `tools/vscode-bbcbasic/` eine schlanke lokale Extension mit
eigener BBC-BASIC-Grammatik. Einmalige Installation:

```
uv run tools/install_vscode_extension.py
```

Danach VS Code neu laden (Ctrl+Shift+P -> "Developer: Reload Window").
Die Extension bietet:

- **Syntax-Highlighting**: REMs, Zeilennummern, Keywords, Strings, Hex.
- **Go to Definition** (Strg+Klick auf `PROC_foo` / `FN_bar` springt
  zum passenden `DEF`, workspace-weit).
- **Outline / Go to Symbol** (Ctrl+Shift+O listet alle PROCs/FNs).
- **Hover-Tooltips** fuer VDU-/PLOT-/`*FX`-Befehle (Maus drueber ->
  Erklaerung + Link auf die offizielle Doku).
- **Code-Snippets** fuer haeufige Muster: `vdu-sprite-move` + Tab ->
  `VDU 23, 27, 13, x%; y%;`, `vdu-sprite-setup` + Tab -> kompletter
  Sprite-Init-Block, `for` + Tab -> FOR/NEXT-Geruest, usw.
- **Toggle Line Comment** (Ctrl+/) setzt `REM` am Zeilenanfang.

Details + Snippet-Liste: [`tools/vscode-bbcbasic/README.md`](tools/vscode-bbcbasic/README.md).

## Debuggen

Drei Ebenen, frei kombinierbar:

1. **BASIC-Level**: `PROC_dbg_trace`, `PROC_dbg_assert`, `PROC_dbg_log` aus
   `lib/debug.bas`. Funktioniert auch auf echter Hardware.
2. **Emulator-Pause**: `PROC_dbg_bp(id)` + `uv run tools/debug.py` oeffnet
   den eZ80-Debugger an der Stelle.
3. **Adress-Breakpoint**: `uv run tools/debug.py -b 0x40000` fuer
   Maschinencode-Schrittausfuehrung.

Details in [docs/DEBUGGING.md](docs/DEBUGGING.md).

## Weiter

- [docs/SETUP.md](docs/SETUP.md)     - Windows-Setup von null
- [docs/WORKFLOW.md](docs/WORKFLOW.md) - Edit/Deploy/Run/Debug-Schleife
- [docs/DEBUGGING.md](docs/DEBUGGING.md) - Alle drei Debug-Ebenen
- [docs/TESTING.md](docs/TESTING.md)   - Tests schreiben
- [docs/RESOURCES.md](docs/RESOURCES.md) - Wichtige Links

## Hinweise

- `.bas`-Dateien haben CRLF-Zeilenenden (von Agon-BBC-BASIC erwartet).
- `autoexec.txt` auf der SD-Karte muss LF haben (Tools regeln das).
- Tastatur-Default ist **deutsch** (`SET KEYBOARD 2`); Override per `--keyboard N`
  bei `run.py` / `debug.py`. Nummern: 0=UK, 1=US, 2=DE, 5=FR, 11=Schweiz-DE, ...
  Siehe [docs/WORKFLOW.md](docs/WORKFLOW.md#tastatur-layout).
- Der Emulator wird **nicht** eingecheckt - er wird beim Setup
  heruntergeladen und entpackt (`emulator/`, gitignored).
- `sdcard/staged/` wird vom Setup erzeugt und ist ebenfalls gitignored.
