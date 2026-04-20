# Workflow

Die Standard-Edit-/Build-/Run-/Debug-Schleife mit AgonBasics.

## Kurzfassung

```
(1) edit beispiele/foo.bas
(2) uv run tools/deploy.py            # beispiele/ -> sdcard/staged/
(3) uv run tools/run.py --program foo.bas
(4) im BBC-BASIC-Prompt:  CHAIN "foo.bas"
(5) bei Bedarf debuggen: uv run tools/debug.py --program foo.bas
```

Fuer Tests:

```
uv run tools/test.py
```

## Ordner

- `beispiele/`  - eigene BASIC-Programme und Assets
- `lib/`         - wiederverwendbare BASIC-Bibliotheken (z. B. `debug.bas`)
- `tests/`       - automatisierte Tests (`test_*.bas`)
- `tools/`       - Python-Skripte (Setup, Deploy, Run, Test, ...)
- `sdcard/staged/` - wird vom Setup gebaut; nicht manuell editieren

**Niemals `sdcard/staged/beispiele/*.bas` editieren** - bei jedem Deploy
wird das ueberschrieben. Quelle ist `beispiele/`.

## Neue Datei anlegen

1. Datei in `beispiele/` anlegen, z. B. `beispiele/meinspiel.bas`.
2. `.bas`-Dateien beginnen immer mit Zeilennummern:
   ```
   10 PRINT "Los geht's"
   20 END
   ```
3. `uv run tools/deploy.py` kopiert die Datei in die gestagte SD-Karte
   mit CRLF-Zeilenenden.
4. `uv run tools/run.py --program meinspiel.bas` startet den GUI-Emulator
   mit `cd beispiele ; bin/bbcbasic` als Autoexec.
5. Im BBC-BASIC-Prompt: `CHAIN "meinspiel.bas"`.

## Debug-Bibliothek verwenden

Am Anfang des Programms:

```
10 REM mein programm
20 REM USES lib/debug
30 PROC_dbg_init("")
40 PROC_dbg_trace("startwert", 42)
50 PROC_dbg_exit(0)
60 END
```

Der Marker `REM USES lib/debug` in Zeile 20 sorgt dafuer, dass
`tools/deploy.py` den Inhalt von `lib/debug.bas` ans Dateiende
anhaengt. Im BBC-BASIC sind PROCs dann verfuegbar.

Siehe [DEBUGGING.md](DEBUGGING.md) fuer alle PROCs und Debug-Ebenen.

## Assets (z. B. Sprites)

Python-Tools erzeugen bei Bedarf Assets:

```
uv run tools/make_ship.py     # erzeugt beispiele/ship.rgba
uv run tools/deploy.py        # kopiert ship.rgba in die staged SD
```

Eigene Asset-Tools gehoeren in `tools/` mit PEP-723-Inline-Dependencies
am Dateianfang.

## Headless vs. GUI

| Modus | Befehl | Vorteile | Nachteile |
|---|---|---|---|
| GUI | `uv run tools/run.py --program X.bas` | Grafik, Sprites, Sound, Tastatur | Interaktiv, nicht skriptbar |
| Headless | `uv run tools/run.py --headless --program X.bas` | Skriptbar, CI-tauglich, stdout einfach abgreifen | Keine Grafik, keine Sprites |

Headless-Programme muessen sich **selbst beenden** (sonst laeuft der
Emulator bis zum Timeout). Dafuer am Ende:

```
PROC_dbg_exit(0)
```

(aus `lib/debug.bas`; aktiviert `OUT (&00), A`, was den Emulator mit
Exit-Code beendet.)

## Tests schreiben

Siehe [TESTING.md](TESTING.md).

## Auf echte Hardware deployen

```
uv run tools/deploy_sdcard.py F:              # Dry-Run (nur anzeigen)
uv run tools/deploy_sdcard.py F: --confirm    # tatsaechlich kopieren
uv run tools/deploy_sdcard.py F: --confirm --mirror  # Ziel spiegeln (loescht Fremddateien!)
```

Windows akzeptiert nur Wechseldatentraeger (`DRIVE_REMOVABLE`). Das
Systemlaufwerk ist zusaetzlich hart blockiert.

## Emulator-Flags durchreichen

Alle nach `--` (oder einfach als freie Argumente) landen beim Emulator:

```
uv run tools/run.py --firmware quark -u
uv run tools/run.py --fullscreen --mode 2
uv run tools/run.py -- --verbose --border ff0000
```

## Typische Iteration

1. Quellcode editieren in VS Code.
2. Ctrl+Shift+B (Task "AgonBasics: Deploy"): Dateien aktualisieren.
3. Task "AgonBasics: Run current .bas (GUI)" oder "(headless)" starten.
4. Fehler? Task "AgonBasics: Debug" (eZ80-Debugger).
5. Tests: Task "AgonBasics: Test" (Ctrl+Shift+P, "Run Test Task").
