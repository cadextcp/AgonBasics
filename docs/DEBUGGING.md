# Debugging

BBC BASIC auf dem Agon hat keinen eingebauten Source-Level-Debugger.
`AgonBasics` bietet drei Ebenen, die sich gut kombinieren lassen.

## Uebersicht

| Ebene | Werkzeug | Wofuer? |
|---|---|---|
| 1 | `lib/debug.bas` (PROC_dbg_trace, _assert, _log) | BASIC-Variablen, Kontrollfluss; funktioniert auch auf echter Hardware |
| 2 | `PROC_dbg_bp(id)` + `uv run tools/debug.py` | Emulator haelt an der Stelle an; eZ80-Debugger oeffnet sich |
| 3 | `uv run tools/debug.py -b 0xADDR` | Hard-Breakpoint auf Maschinenebene (assembler/inline-asm) |

Alle Ebenen nutzen intern die [Debug-I/O-Ports des Emulators](https://github.com/tomm/fab-agon-emulator#debug-io-space):

- `OUT (&00), A` - beendet den Emulator, `A` ist der Exit-Code
- `OUT (&10), A` - Breakpoint (benoetigt Emulator mit `-d`)
- `OUT (&20), A` - CPU-Zustand in die Debugger-Konsole dumpen

Auf echter Hardware sind diese Ports unbelegt und die OUT-Instruktionen
haben keinen Effekt (ausser minimalem CPU-Overhead). Code bleibt also
portabel.

---

## Ebene 1: BASIC-Trace-Bibliothek

**Wann benutzen?** Immer. Schneller Einblick in Variablenwerte und
Kontrollfluss ohne Emulator-Debugger.

### Aktivieren

Im eigenen Programm den Marker setzen:

```
20 REM USES lib/debug
```

Der `tools/deploy.py`-Schritt haengt `lib/debug.bas` an die Datei an,
bevor sie in die SD-Karte gelangt.

### Prozeduren

| Aufruf | Wirkung |
|---|---|
| `PROC_dbg_init("")` | initialisiert; ohne Argument kein Logfile |
| `PROC_dbg_init("log.txt")` | zusaetzlich Logfile auf der SD-Karte |
| `PROC_dbg_close` | Logfile schliessen (meist nicht noetig) |
| `PROC_dbg_log("msg")` | freie Textzeile, Zeitstempel wird angefuegt |
| `PROC_dbg_trace("x%", x%)` | Variable labeln und loggen |
| `PROC_dbg_assert(cond, "msg")` | bei `cond=0`: `msg` loggen, `=== TEST FAIL ===` drucken, Emulator mit Exit-Code 1 beenden |
| `FN_dbg_time` | Centisekunden seit `PROC_dbg_init` |

### Hold-Mode: Fenster nach PROC_dbg_exit offen halten

Beim interaktiven Debuggen in der GUI ist es lästig, dass
`PROC_dbg_exit` (auch von `PROC_dbg_assert` intern aufgerufen) das
Emulator-Fenster sofort schließt — man sieht die Fehlermeldung nur
kurz, dann ist alles weg.

Abhilfe: `--hold` an `run.py` oder `debug.py`:

```
uv run tools/run.py   --program summe_bug.bas --hold
uv run tools/debug.py --program summe_bug.bas --hold
```

Der Flag patcht die gestagte Programmdatei so, dass `PROC_dbg_exit`
nur loggt und `END` aufruft statt den Emulator zu terminieren. Du
landest im BBC-BASIC-Prompt `>` und kannst Variablen inspizieren,
z. B.:

```
> PRINT f%
0
> PRINT i%
5
```

Der Patch überlebt nur bis zum nächsten `uv run tools/deploy.py`
(oder Test-Lauf), dann ist alles wieder normal.

**Nicht benutzen** in automatisierten Tests — dort soll
`PROC_dbg_exit` den Emulator wirklich beenden.

### Syntax-Smoke-Test fuer Grafik-Programme

Sobald ein Programm `MODE 8` aufruft, verschluckt der Fake-VDP des
CLI-Emulators alle Syntax-Fehlermeldungen (sie gehen als VDU-Bytes an
die Grafik statt auf stdout). Das macht headless-Debugging muehsam.

Workaround: **alle PROCs vor `MODE` einmal aufrufen**. So crasht das
Programm in stdout, bevor die VDP die Ausgabe schluckt. Beispiel dafuer:
`beispiele/breakout_smoke.bas` — laedt die gleichen Globals wie
`breakout.bas`, ruft aber jede PROC einmal mit Dummy-Parametern auf
und beendet mit `=== TEST PASS ===`.

Typischer Ablauf beim Entwickeln eines Grafik-Spiels:

1. Logik in Prozeduren kapseln.
2. Ein `_smoke.bas` schreiben, das die Globals initialisiert und alle
   PROCs einmal anruft (ohne MODE).
3. `uv run tools/run.py --headless --program spiel_smoke.bas` →
   zeigt Syntax-Fehler direkt auf stdout.
4. Wenn gruen: `uv run tools/run.py --program spiel.bas` im GUI.

### Beispiel

```
10 REM mein programm
20 REM USES lib/debug
30 PROC_dbg_init("")
40 x% = 0
50 FOR i% = 1 TO 5
60   x% = x% + i%
70   PROC_dbg_trace("x% in iter " + STR$(i%), x%)
80 NEXT i%
90 PROC_dbg_assert(x% = 15, "Summe muss 15 sein")
100 PRINT "Fertig"
110 END
```

Ausgabe:

```
[dbg] init t=0 log=-
[dbg t=0] x% in iter 1 = 1
[dbg t=0] x% in iter 2 = 3
[dbg t=1] x% in iter 3 = 6
[dbg t=1] x% in iter 4 = 10
[dbg t=2] x% in iter 5 = 15
Fertig
```

---

## Ebene 2: Emulator-Breakpoint aus BASIC

**Wann benutzen?** Zu einem bestimmten Zeitpunkt im BASIC-Programm an der
Emulatorkonsole anhalten, um Speicher / Register zu untersuchen.

### Vorbereitung

Emulator **mit** Debugger starten:

```
uv run tools/debug.py --program mein.bas
```

Im Programm an der interessanten Stelle:

```
100 PROC_dbg_bp(1)
```

Wenn der eZ80 die interne `OUT (&10), A`-Instruktion ausfuehrt, halten
Emulator UND Terminal an. Im Terminal erscheint der Debug-Prompt:

```
DEBUG>
```

### Debug-Befehle

```
help            Uebersicht
step            Eine Instruktion ausfuehren
continue        Lauf fortsetzen
registers       CPU-Register anzeigen
memory 40000 64 Speicher ab &40000, 64 Bytes
break 40100     Breakpoint bei Adresse
trace           Instruktions-Trace umschalten
```

Siehe auch: [fab-agon-emulator README - Z80 debugger](https://github.com/tomm/fab-agon-emulator#the-z80-debugger).

### Register-Dump ohne Anhalten

`PROC_dbg_regs(id)` schreibt auf Port `&20-&2F`. Der Debugger dumpt den
aktuellen CPU-Zustand in die Konsole **ohne** anzuhalten. Gut fuer
periodische Momentaufnahmen:

```
200 FOR i% = 1 TO 10 : PROC_dbg_regs(i%) : NEXT
```

---

## Ebene 3: Adress-Breakpoints (Maschinencode)

**Wann benutzen?** Debugging von inline-Assembler oder ganzen
`.bin`-Programmen (ez80asm-Output).

```
uv run tools/debug.py --program assembler.bas -b 0x40000 -b 0x40050
```

`0x40000` ist die Basis-RAM-Adresse fuer BBC BASIC's Code-Bereich.
Konkrete Adressen ergeben sich aus:

- `PRINT ~code%` im BBC-BASIC-Prompt, um den Start-Offset deines
  inline-Asm-Blocks zu erhalten.
- Oder aus der ez80asm-Listing-Datei bei externen Assembler-Programmen.

Der Emulator halt bei Erreichen an. Der Debugger-Prompt laesst
`step`/`continue`/`memory` zu.

---

## Debug-Flow: schnelle Entscheidung

```
Fehler im BASIC-Code?
  ├── Variablenwert unklar?         -> PROC_dbg_trace
  ├── Logik-Zweig nie durchlaufen? -> PROC_dbg_log an jedem Zweig
  ├── Irgendwas stimmt nicht?       -> PROC_dbg_assert
  └── Tiefer reingucken noetig?     -> PROC_dbg_bp + debug.py

Fehler im inline-Assembler?
  ├── Routine wird aufgerufen?      -> PROC_dbg_bp direkt vor CALL
  ├── Register bei Eintritt?        -> PROC_dbg_regs vor CALL
  └── Instruktionsfluss?             -> debug.py -b 0xADDR + step
```

## Auf echter Hardware

- Ebene 1 (trace/assert/log) funktioniert unveraendert. Die
  `OUT`-Instruktionen hinter `PROC_dbg_bp/_regs/_exit` sind harmlose
  No-ops, weil die betreffenden I/O-Ports auf dem eZ80F92 unbelegt
  sind.
- Ebenen 2 und 3 wirken nur im Emulator.

Deshalb: **derselbe Code laeuft auf Emulator UND Board**.

## Exit-Codes fuer CI

`PROC_dbg_exit(0)` beendet den Emulator mit Exit-Code 0 (Erfolg).
`PROC_dbg_exit(1)` entsprechend mit 1 (Fehler). Der Headless-CLI-Emulator
uebernimmt diesen Wert als Prozess-Exit-Code - darauf bauen
`tools/test.py` und die CI auf.

## Weiterfuehrende Doku

Die offizielle Agon-Platform-Doku hat tiefere Referenzen:

- [MOS API (RST 08h, Syscalls)](https://agonplatform.github.io/agon-docs/mos/API/) - relevant fuer alles was tiefer als BASIC ist
- [MOS System Variables](https://agonplatform.github.io/agon-docs/mos/System-Variables/) - SYSVARS-Block, Echtzeit-Uhr, Tastatur-State
- [Theory of operation](https://agonplatform.github.io/agon-docs/Theory-of-operation/) - Architektur eZ80 + ESP32, hilft beim Verstaendnis der Adressraeume
- [fab-agon-emulator Debug-I/O](https://github.com/tomm/fab-agon-emulator#debug-io-space) - die drei Ports `&00/&10/&20`, wie sie intern funktionieren
- Quick-Lookup lokal: [REFERENCE.md](REFERENCE.md) (MOS-Syscalls, VDU-Codes, Speicherkarte)
- Kompletter Doku-Baum: [RESOURCES.md](RESOURCES.md)
