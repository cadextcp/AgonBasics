# Tests schreiben

Automatisierte Tests in BBC BASIC laufen headless im
`agon-cli-emulator.exe`. `tools/test.py` findet `tests/test_*.bas`,
staged sie (inkl. Debug-Library), startet den Emulator und wertet das
Ergebnis aus.

## Minimales Test-Template

`tests/test_foo.bas`:

```
10 REM test_foo.bas - Beschreibung
20 REM USES lib/debug
30 PROC_dbg_init("")
40 :
50 REM --- eigene Logik ---
60 ergebnis% = 1 + 1
70 PROC_dbg_assert(ergebnis% = 2, "1+1 muss 2 sein")
80 :
90 PRINT "=== TEST PASS ==="
100 PROC_dbg_exit(0)
110 END
```

## Pflichtmarkierungen

Der Runner erkennt **nur** diese Marker im emittierten stdout:

| Marker | Wirkung |
|---|---|
| `=== TEST PASS ===` | Test gilt als bestanden (falls kein Fail-Marker folgt) |
| `=== TEST FAIL ===` | Test gilt als fehlgeschlagen |

**Muss** per PRINT ausgegeben werden. Ausserdem **muss** am Ende
`PROC_dbg_exit(0)` stehen (damit sich der Emulator beendet - sonst
Timeout).

## Optional: Erwartete Ausgabe vergleichen

Wenn Ausgabe bitgenau verifiziert werden soll:

1. In der Test-Datei die Nutzausgabe zwischen Markern drucken:
   ```
   120 PRINT "=== OUTPUT BEGIN ==="
   130 PRINT "1 + 1 = "; STR$(ergebnis%)
   140 PRINT "=== OUTPUT END ==="
   ```
2. Datei `tests/expected/test_foo.txt` mit genau dieser Ausgabe anlegen
   (LF-Zeilenenden):
   ```
   1 + 1 = 2
   ```
3. Der Runner extrahiert den Text zwischen den Markern und diff'ed gegen
   die Erwartungsdatei.

Wenn keine Erwartungsdatei existiert, wird der Test nur ueber das
`=== TEST PASS ===`-Flag bewertet.

## Expected-Datei automatisch erzeugen

Beim initialen Anlegen eines Tests:

```
uv run tools/test.py --update
```

Fehlende `tests/expected/*.txt` werden aus der aktuellen Ausgabe
erzeugt. **Niemals in CI** mit `--update` laufen - der Test wuerde sich
selbst reparieren.

## Deterministische Ausgabe

BBC BASIC formatiert Integer standardmaessig mit Feldbreite `@%=10`
(Leerzeichen-Padding). Das fuehrt zu brittle-expected-Dateien.

**Empfehlung**: `STR$(wert)` verwenden, um die Stringdarstellung ohne
Padding zu bekommen:

```
130 PRINT "x = "; STR$(x%)     ->    x = 42
130 PRINT "x = "; x%           ->    x =         42
```

Fuer Fliesskommazahlen analog `STR$`.

## Flags

```
uv run tools/test.py                    # alle Tests
uv run tools/test.py --filter schleife  # nur tests/test_schleife*.bas
uv run tools/test.py --verbose          # kompletter stdout pro Test
uv run tools/test.py --update           # fehlende expected erzeugen
uv run tools/test.py --timeout 60       # pro Test max. 60s
```

## Wie der Runner entscheidet

Pro Test:

1. Datei nach `sdcard/staged/beispiele/test_X.bas` stagen (mit
   lib-Inlining falls `REM USES lib/debug`).
2. `agon-cli-emulator.exe` starten, stdin piped:
   ```
   .
   cd beispiele
   bin/bbcbasic
   CHAIN "test_X.bas"
   ```
3. stdout einsammeln, bis:
   - der Prozess sich per `OUT (&00), A` beendet (via `PROC_dbg_exit`), **oder**
   - der Timeout greift.
4. Auswertung:
   - `=== TEST FAIL ===` gesehen  -> Fail.
   - `=== TEST PASS ===` fehlt    -> Fail.
   - Expected-Datei und OUTPUT-Block vorhanden und unterschiedlich  -> Fail.
   - sonst Pass.

## Tests, die Grafik brauchen

Der **Headless-CLI-Emulator hat KEIN VDP**. `MODE`, `PLOT`, `DRAW`,
Sprite-VDU-Sequenzen funktionieren dort nicht.

Strategien:

- Trennen: Grafik-intensive Logik in PROCs packen. In Tests nur die
  rechnerische Kernlogik aufrufen.
- Oder: Tests uebersehen die Grafik und verifizieren nur Seiteneffekte
  (Variablenwerte, Dateiausgabe).

Visuelle Regression-Tests via Screenshots waeren theoretisch moeglich
(GUI-Emulator + Screen-Capture), sind aber in diesem Template nicht
vorgesehen.

## CI (GitHub Actions)

`.github/workflows/test.yml` laeuft auf `windows-latest`:

```
uv run tools/setup.py --no-interactive
uv run tools/deploy.py
uv run tools/test.py --verbose
```

Ein Test-Fehler -> Workflow schlaegt fehl.

## Weiterlesen

- [BBC Basic for Agon](https://agonplatform.github.io/agon-docs/BBC-BASIC-for-Agon/) - Sprachreferenz fuer Testkoerper
- [Programming](https://agonplatform.github.io/agon-docs/Programming/) - was sich testen laesst und was nicht
- [REFERENCE.md](REFERENCE.md) - `STR$`, `ERR`/`ERL`, VDU/PLOT-Codes
- [DEBUGGING.md](DEBUGGING.md) - die Debug-Ebenen, die man in Tests mischen kann
