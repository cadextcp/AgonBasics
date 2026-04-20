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
| `tests/` | `test_*.bas` + erwartete Ausgaben fuer `tools/test.py` |
| `tools/` | Python-Skripte: `setup`, `deploy`, `run`, `debug`, `test`, `deploy_sdcard`, `make_ship` |
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
