# AGENTS.md

Projekt-Regeln für Agenten und Mitwirkende, die in diesem Repository arbeiten.

## Worum es geht

`AgonBasics` ist ein Basisprojekt für BBC-BASIC-Entwicklung auf dem Agon Light /
Console8. Ziel ist: clonen, `uv run tools/setup.py`, loslegen. Das beinhaltet
den Emulator, eine batteriebetriebene Popup-MOS-SD-Karte, Beispiele, eine
BASIC-Debug-Bibliothek und einen Headless-Testrunner.

## Sprach- und Stilregeln

- Folder- und Dateinamen, Doku und `REM`-Kommentare sind **deutsch**.
- Python-Code, CLI-Flags und Commit-Messages dürfen englisch sein.
- BBC-BASIC-Quelltext (`*.bas`) braucht **Zeilennummern** (10, 20, 30, ...).
  Das ist keine Stilvorgabe, sondern vom Interpreter erzwungen.

## Dateiformate und Zeilenenden

- `*.bas` -> **CRLF** (BBC BASIC für Agon erwartet das).
- `autoexec.txt` auf der SD-Karte -> **LF** (sonst bootet es kommentarlos nicht).
- Python und Markdown -> LF.
- `.vscode/settings.json` setzt die `files.eol`-Assoziationen entsprechend.

## Struktur (Kurzfassung)

```
beispiele/    BASIC-Beispielprogramme (CRLF)
lib/          Wiederverwendbare BASIC-Bibliotheken (debug.bas etc.)
tests/        Automatische BASIC-Tests + expected/ Referenzausgaben
tools/        Python-Tooling (uv run, inline-deps PEP 723)
docs/         Deutsche Dokumentation
emulator/     (gitignored) Vom Setup entpackter Emulator
sdcard/staged/(gitignored) Zusammengefuegte SD-Karte: Popup MOS + beispiele + lib
```

## Tool-Konventionen

Alles Host-seitige Tooling liegt in `tools/` und wird mit `uv` ausgefuehrt:

```
uv run tools/setup.py         # einmaliges Setup: Emulator + SD-Karte
uv run tools/deploy.py        # beispiele/+lib/ -> sdcard/staged/
uv run tools/run.py           # GUI-Emulator starten
uv run tools/debug.py         # Emulator mit eZ80-Debugger
uv run tools/test.py          # Headless-Tests
uv run tools/deploy_sdcard.py # auf echte microSD kopieren
```

Abhaengigkeiten werden per **PEP 723 inline-Script-Metadaten** am Dateianfang
deklariert, nicht in einer zentralen `requirements.txt`. Beispiel:

```python
# /// script
# requires-python = ">=3.11"
# dependencies = ["requests>=2.31"]
# ///
```

## Verifikationsbefehle

Vor jedem Commit sollte mindestens das hier gruen sein:

```
uv run tools/test.py
```

Bei Aenderungen am Setup-/Run-Flow zusaetzlich:

```
uv run tools/setup.py --no-interactive
uv run tools/run.py --headless --program hello.bas
```

Die CI (`.github/workflows/test.yml`) faehrt diese Befehle auf einem
Windows-Runner.

## Debug-Ebenen (Schnellreferenz)

1. **BASIC-Level**: `lib/debug.bas` mit `PROC_dbg_trace`, `PROC_dbg_assert`.
2. **Emulator-Pause**: `PROC_dbg_bp(id)` (inline `OUT (&10), A`) in Kombination
   mit `uv run tools/debug.py` -> oeffnet den eZ80-Debugger bei Erreichen.
3. **Adress-Breakpoint** (reines Maschinencode-Debugging):
   `uv run tools/debug.py -b 0x40000 -b 0x40100`.

Details in `docs/DEBUGGING.md`.

## Destruktive Operationen

- `tools/deploy_sdcard.py` schreibt auf ein angegebenes Laufwerk (physische
  microSD). Immer mit `--confirm`. Niemals das Systemlaufwerk akzeptieren.
- Submodul-Entfernungen, `git push --force`, `rm -rf` nur nach expliziter
  Nutzer-Freigabe.

## Was nicht commitet wird

- `emulator/` (vom Setup erzeugt, ~30 MB entpackt)
- `sdcard/staged/` (vom Setup erzeugt)
- `.venv/`, `__pycache__/`, `*.pyc`

Siehe `.gitignore`.

## Externe Abhaengigkeiten

- `fab-agon-emulator` v1.1.3 Windows x64 ZIP aus GitHub Releases
  (`https://github.com/tomm/fab-agon-emulator/releases`).
- Popup MOS (im v1.1.3-Zip enthalten, Upstream:
  `https://github.com/tomm/popup-mos`).

Die Versionen und SHA-256-Pruefsummen stehen in `tools/setup.py`. Upgrades
erfolgen dort.

## Offizielle Referenz-Doku

Die **kanonische Quelle** fuer alles, was nicht in diesem Repo
dokumentiert ist:

- Rendered: <https://agonplatform.github.io/agon-docs/>
- Source (GitHub): <https://github.com/AgonPlatform/agon-docs>
- Offline: `uv run tools/fetch_docs.py` legt einen git-Clone unter
  `docs/agon-platform-docs/` an (gitignored).

Daily-driver Seiten:

- MOS API           <https://agonplatform.github.io/agon-docs/mos/API/>
- VDU Commands      <https://agonplatform.github.io/agon-docs/vdp/VDU-Commands/>
- PLOT Commands     <https://agonplatform.github.io/agon-docs/vdp/PLOT-Commands/>
- Screen Modes      <https://agonplatform.github.io/agon-docs/vdp/Screen-Modes/>
- BBC Basic         <https://agonplatform.github.io/agon-docs/BBC-BASIC-for-Agon/>
- Theory of op.     <https://agonplatform.github.io/agon-docs/Theory-of-operation/>

Lokale Zusammenstellung mit Links: `docs/RESOURCES.md`.
Lokaler Spickzettel: `docs/REFERENCE.md`.

**Regel fuer Agenten/Mitwirkende:** Bei Aenderungen am Funktionsverhalten
immer zuerst die offizielle Doku konsultieren. Wenn das Verhalten auf dem
Agon dort anders dokumentiert ist als im Repo implementiert, gilt die
offizielle Doku als Referenz - Implementierung anpassen, nicht die Doku
"hinbiegen".
