# Quick-Reference

Kuratierter Spickzettel mit den Befehlen, die im BBC-BASIC-Alltag am
haeufigsten vorkommen. **Die kanonische Quelle** ist immer die offizielle
[Agon-Platform-Doku](https://agonplatform.github.io/agon-docs/). Jede
Zeile unten deep-linked zurueck dorthin.

Siehe auch: [RESOURCES.md](RESOURCES.md) fuer die vollstaendige
Dokumentationsstruktur.

---

## VDU Commands (0-31, 127)

Offizielle Referenz: <https://agonplatform.github.io/agon-docs/vdp/VDU-Commands/>

| Code | Wirkung | BBC-BASIC-Aequivalent |
|---|---|---|
| `VDU 0` | Null / no-op | - |
| `VDU 4` / `VDU 5` | Text am Text- / Grafik-Cursor ausgeben | `*FX ...` |
| `VDU 7` | BEL (kurzer Piep) | `SOUND` |
| `VDU 12` | Text-Bereich loeschen | `CLS` |
| `VDU 13` | Carriage return | `PRINT` |
| `VDU 16` | Grafikbereich loeschen | `CLG` |
| `VDU 17, c` | Textfarbe setzen | `COLOUR c` |
| `VDU 18, m, c` | Grafikfarbe + Modus | `GCOL m, c` |
| `VDU 19, l, p, r, g, b` | Logische Palette definieren | `COLOUR l, r, g, b` |
| `VDU 22, n` | Bildschirmmodus waehlen | `MODE n` |
| `VDU 23, 0, <cmd>, ...` | VDP-System-Kommandos | siehe [System Commands](https://agonplatform.github.io/agon-docs/vdp/System-Commands/) |
| `VDU 23, 1, n` | Cursor zeigen/ausblenden | `*FX 4` |
| `VDU 23, 27, <cmd>, ...` | Bitmaps/Sprites (siehe unten) | - |
| `VDU 24, l; b; r; t;` | Grafik-Viewport setzen | - |
| `VDU 25, mode, x; y;` | PLOT (siehe unten) | `PLOT mode, x, y` |
| `VDU 28, l, b, r, t` | Text-Viewport setzen | - |
| `VDU 29, x; y;` | Grafik-Ursprung verschieben | `ORIGIN x, y` |
| `VDU 30` | Text-Cursor nach oben links | `CLS` lite |
| `VDU 31, x, y` | Text-Cursor auf (x, y) | `PRINT TAB(x, y);...` |
| `VDU 127` | Backspace | - |

Beispiel aus `beispiele/sprite.bas`:

```basic
40 VDU 23, 27, 0, 0      : REM Select Bitmap 0
50 VDU 23, 27, 1, 16; 16;  : REM Define 16x16 bitmap
```

Siehe [Bitmaps and Sprites API](https://agonplatform.github.io/agon-docs/vdp/Bitmaps-API/).

---

## PLOT-Befehle (`VDU 25, code, x; y;`)

Offizielle Referenz: <https://agonplatform.github.io/agon-docs/vdp/PLOT-Commands/>

Jeder Befehl hat 8 Varianten, in denen die unteren 3 Bits den
Zeichen-Modus steuern (`.. + 0` = Relativ / Normal, weitere = andere
Paint-Modi - siehe Doku).

| Code-Bereich | Operation |
|---|---|
| `&00-&07` | Linie (volle, beide Endpunkte) |
| `&08-&0F` | Linie (ohne Endpunkt) |
| `&10-&17` | Punktierte Linie (VDP 2.7.0+) |
| `&20-&27` | Linie ohne Startpunkt |
| `&40-&47` | Punkt plotten |
| `&48-&4F` | Line-fill horizontal bis Hintergrund (§§) |
| `&50-&57` | Dreieck ausgefuellt |
| `&58-&5F` | Line-fill horizontal, rechts bis Hintergrund (§§) |
| `&60-&67` | Rechteck ausgefuellt |
| `&68-&6F` | Line-fill horizontal bis Vordergrund (§§) |
| `&70-&77` | Parallelogramm ausgefuellt |
| `&80-&87` | Flood-fill zum aktuellen Farbbereich |
| `&88-&8F` | Flood-fill innerhalb einer bestimmten Farbe |
| `&90-&97` | Kreis (Umriss) |
| `&98-&9F` | Kreis (gefuellt) |
| `&A0-&B7` | Boegen, Segmente, Sektoren (VDP 2.8.0+) |
| `&B8-&BF` | Rechteck kopieren/verschieben |
| `&C0-&CF` | Ellipsen |
| `&D8-&DF` | Path-Fill (experimentell, VDP 2.8.0+) |
| `&E8-&EF` | Bitmap plotten |

Beispiel (`beispiele/dreieck.bas`):

```basic
10 MODE 8
20 GCOL 0, 2
30 MOVE 100, 100
40 MOVE 300, 100
50 PLOT 85, 200, 300   : REM 85 = &55 = Triangle-Fill (relative to last two)
```

---

## Bildschirmmodi (Auszug)

Offizielle Referenz: <https://agonplatform.github.io/agon-docs/vdp/Screen-Modes/>

Ab VDP 1.04 (Standard im fab-agon-emulator v1.1.3):

| Mode | Aufloesung | Farben | Hz | Anmerkung |
|---|---|---|---|---|
| 0 | 640×480 | 16 | 60 | Default |
| 1 | 640×480 | 4 | 60 | |
| 2 | 640×480 | 2 | 60 | schnellste Textausgabe |
| 3 | 640×240 | 64 | 60 | |
| 4 | 640×240 | 16 | 60 | |
| 8 | 320×240 | 64 | 60 | Retro-Look, viele Farben |
| 12 | 320×200 | 64 | 70 | CGA-aehnlich |
| 16 | 800×600 | 4 | 60 | |
| 18 | 1024×768 | 2 | 60 | |

`MODE n + 128` = doppelgepuffert (flackerfrei via `VDU 23,0,&C3`).

---

## MOS-API-Syscalls (RST 08h)

Offizielle Referenz: <https://agonplatform.github.io/agon-docs/mos/API/>

Aufruf aus Assembler: `LD A, <syscall_nr>; RST.LIL &08` (ADL) bzw.
`RST &08` (Z80). Von BBC BASIC meist nur aus inline-Assembler interessant.

### Core (0x00-0x24)

| Nr | Name | Zweck |
|---|---|---|
| 0x00 | `mos_getkey` | Tastaturzeichen holen (blocking) |
| 0x01 | `mos_load` | Datei laden |
| 0x02 | `mos_save` | Datei speichern |
| 0x03 | `mos_cd` | Arbeitsverzeichnis wechseln |
| 0x04 | `mos_dir` | Verzeichnis auflisten |
| 0x05 | `mos_del` | Datei loeschen |
| 0x07 | `mos_mkdir` | Verzeichnis anlegen |
| 0x08 | `mos_sysvars` | Pointer auf SYSVARS-Block |
| 0x0A | `mos_fopen` | Datei oeffnen |
| 0x0B | `mos_fclose` | Datei schliessen |
| 0x0C | `mos_fgetc` | Byte lesen |
| 0x0D | `mos_fputc` | Byte schreiben |
| 0x0E | `mos_feof` | EOF pruefen |
| 0x10 | `mos_oscli` | MOS-CLI-Befehl ausfuehren |
| 0x12 | `mos_getrtc` | RTC lesen |
| 0x1A | `mos_fread` | Block lesen |
| 0x1B | `mos_fwrite` | Block schreiben |
| 0x1C | `mos_flseek` | Dateiposition setzen |

### String / Variablen (0x28-0x36)

| Nr | Name |
|---|---|
| 0x28 | `mos_pmatch` |
| 0x29 | `mos_getargument` |
| 0x30 | `mos_setvarval` |
| 0x31 | `mos_readvarval` |
| 0x36 | `mos_evaluateexpression` |

### Pfade (0x38-0x3C)

| Nr | Name |
|---|---|
| 0x38 | `mos_resolvepath` |
| 0x39 | `mos_getdirforpath` |
| 0x3A | `mos_getleafname` |
| 0x3B | `mos_isdirectory` |

### FatFS (0x80-0xA6)

Direkter Zugriff auf FatFS (analog `f_open`, `f_read`, ...). Siehe
Tabelle in der Doku — die Namen sind 1:1 die FatFS-Funktionen mit
`ffs_`-Praefix.

### RST-Opcodes (Z80-Assembly)

| Opcode | Zweck |
|---|---|
| `RST 08h` | MOS-Syscall ausfuehren (A = Syscall-Nr.) |
| `RST 10h` | Ein Zeichen an VDP |
| `RST 18h` | Stream an VDP (MOS 1.03+) |
| `RST 38h` | Crash-Report (MOS 2.3.0+) |

---

## Speicherkarte (Agon Light)

Quelle: [Theory of operation](https://agonplatform.github.io/agon-docs/Theory-of-operation/)
und <https://github.com/envenomator/Agon/blob/master/Memory%20map.png>.

| Adresse (24-Bit) | Inhalt |
|---|---|
| `&000000 - &01FFFF` | MOS (Flash-ROM) |
| `&040000 - &0AFFFF` | User-RAM - hier laufen BBC BASIC und `.bin`-Programme |
| `&0B0000 - `…       | Module, Scratch, MOS-CLI-Utils |
| `&0BC000 - &0BFFFF` | MOS Global Heap / Stack / SYSVARS |
| `&FFE000 - &FFFFFF` | On-Chip-SRAM (8 KB) |

`P% = &40000` ist der Start fuer BBC-BASIC-inline-Assembler, wie in
`beispiele/assembler.bas`.

---

## Debug-I/O-Ports (fab-agon-emulator)

Quelle: <https://github.com/tomm/fab-agon-emulator#debug-io-space>

| Port | Wirkung (nur Emulator) | Nutzung in `lib/debug.bas` |
|---|---|---|
| `OUT (&00), A` | Emulator beenden, Exit-Code = A | `PROC_dbg_exit(code%)` |
| `OUT (&10..&1F), A` | Breakpoint (nur mit `-d`) | `PROC_dbg_bp(id%)` |
| `OUT (&20..&2F), A` | CPU-Zustand dumpen (nur mit `-d`) | `PROC_dbg_regs(id%)` |

Auf echter Hardware unbelegt - die `OUT`-Instruktionen werden ignoriert,
so dass derselbe BASIC-Code auf Emulator UND Board laeuft.

---

## BBC-BASIC-Kurzbefehle

Siehe offizielle Einzelseite: <https://agonplatform.github.io/agon-docs/BBC-BASIC-for-Agon/>

Schnellwahl:

| Syntax | Zweck |
|---|---|
| `PRINT x; STR$(y)` | Ausgabe ohne feste Feldbreite (deterministisch fuer Tests) |
| `CHAIN "file.bas"` | Datei laden und ausfuehren (statt LOAD + RUN) |
| `*CD beispiele` | MOS-Kommando aus BBC BASIC |
| `OPENIN`/`OPENOUT`/`OPENUP` | Datei oeffnen (lesen / schreiben / anhaengen) |
| `BPUT#h, byte` | Byte in Datei-Handle h schreiben |
| `BGET#h` | Byte aus Handle h lesen |
| `CLOSE #h` | Handle schliessen |
| `CLOSE #0` | Alle offenen Handles schliessen |
| `DIM arr%(n)` | Integer-Array der Groesse n+1 |
| `DIM buf% n` | Bytebuffer von n+1 Bytes (Adresse in `buf%`) |
| `?addr`, `addr?n` | 1 Byte lesen/schreiben |
| `!addr`, `addr!n` | 4 Bytes lesen/schreiben |
| `[ OPT p% ... ]` | Inline-eZ80-Assembler-Block (2-Pass: `FOR p%=0 TO 3 STEP 3`) |

---

## BBC-BASIC-Fehlernummern (Auszug)

BBC BASIC Manual: <https://oldpatientsea.github.io/agon-bbc-basic-manual/0.1/index.html>

| Nr | Bedeutung |
|---|---|
| 5 | `Missing ,` |
| 6 | `Type mismatch` |
| 14 | `Bad key` |
| 17 | `Escape` (auch von `PROC_dbg_assert` geworfen) |
| 18 | `Division by zero` |
| 19 | `String too long` |
| 22 | `Too many FOR loops` |
| 23 | `No REPEAT` |
| 26 | `No such variable` |
| 27 | `Missing (` |
| 29 | `No such FN/PROC` |
| 41 | `No such line` |
| 42 | `Out of DATA` |
| 190 | `Bad floating point` |

In `ON ERROR`-Handlern: `ERR` gibt die Nummer, `ERL` die Zeile.

---

## Nicht-offizielle, aber nuetzliche Spickzettel

- **Sprite-Format**: RGBA8888, Byte-Order pro Pixel ist **A, B, G, R**
  (nicht R, G, B, A!). `tools/make_ship.py` demonstriert das.
  Offizielle Doku: [Bitmaps API](https://agonplatform.github.io/agon-docs/vdp/Bitmaps-API/).
- **autoexec.txt-Pflichten**: LF-Zeilenenden, UTF-8 / ASCII, keine BOM.
- **Tastatur-Scancodes**: siehe [Keyboard Input](https://agonplatform.github.io/agon-docs/mos/Keyboard/).
